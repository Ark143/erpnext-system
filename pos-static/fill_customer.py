import json, sys, urllib.request, urllib.parse, http.cookiejar, os, time
from concurrent.futures import ThreadPoolExecutor
BASE = "https://demoerpnext.s.frappe.cloud"
USR = os.environ.get("CLOUD_USR"); PWD = os.environ.get("CLOUD_PWD")
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def post(path, payload, csrf=None):
    req = urllib.request.Request(BASE+path, json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Accept","application/json")
    if csrf: req.add_header("X-Frappe-CSRF-Token", csrf)
    try:
        r = op.open(req, timeout=120); return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read().decode())
        except Exception: body = {"error": e.reason}
        return e.code, body
    except Exception as e:
        return "ERR", {"error": str(e)}

def get_csrf():
    s,j = post("/api/method/login", {"usr":USR,"pwd":PWD})
    if s!=200: print("LOGIN FAIL", s); sys.exit(1)
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": return c.value

csrf = get_csrf()
print("login OK (fill missing customers)", flush=True)

REMAP = {
    "Customer": {
        "customer_group": {"All Customer Groups": "Individual", "Commercial": "Commercial", "Individual": "Individual"},
        "territory": {"All Territories": "Philippines"},
    }
}
STRIP = ["creation","modified","modified_by","owner","idx","docstatus","lft","rgt","old_parent",
         "_comments","_assign","_user_tags","_liked_by","parent","parentfield","parenttype"]

# 1) load source customer records keyed by name
recs = json.load(open("pos-static/export/Customer.json", encoding="utf-8"))
src = {r["name"]: r for r in recs}
print(f"source customers: {len(src)}", flush=True)

# 2) fetch cloud customer names via pagination
cloud_names = set()
start = 0
while True:
    s,j = post("/api/method/frappe.client.get_list",
               {"doctype":"Customer","fields":["name"],"limit_page_length":500,"limit_start":start}, csrf)
    page = j.get("message") or []
    if s!=200 or not page:
        break
    for g in page: cloud_names.add(g["name"])
    if len(page) < 500: break
    start += 500
print(f"cloud customers: {len(cloud_names)}", flush=True)

missing = [name for name in src if name not in cloud_names]
print(f"MISSING to fill: {len(missing)}", flush=True)

# 3) insert missing
ok=dup=linkfail=err=0; failures=[]
def clean(r):
    doc = {k:v for k,v in r.items() if k not in STRIP and v not in (None,"")}
    doc["doctype"]="Customer"
    for fld,mp in REMAP["Customer"].items():
        if doc.get(fld) in mp: doc[fld]=mp[doc[fld]]
    return doc
def do_one(name):
    doc = clean(src[name])
    for attempt in range(8):
        s,j = post("/api/method/frappe.client.insert", {"doc": doc}, csrf)
        if s==200: return "ok"
        if s==409: return "dup"
        if s==403: return "perm"
        if s==429: time.sleep(2*(attempt+1)); continue
        ex=str(j.get("exception") or j.get("_error_message") or j.get("message") or j.get("error"))
        if "LinkValidationError" in ex or "could not find" in ex.lower() or "Group type" in ex:
            return ("linkfail", ex[:160])
        if s in (417,"ERR") and attempt < 7:
            time.sleep(2); continue
        return ("err", f"{s} {ex[:140]}")
    return "err"
with ThreadPoolExecutor(max_workers=8) as ex:
    for i,res in enumerate(ex.map(do_one, missing), 1):
        if res=="ok": ok+=1
        elif res=="dup": dup+=1
        elif res=="perm": print("PERM 403", flush=True); break
        elif isinstance(res,tuple) and res[0]=="linkfail": linkfail+=1; failures.append(res[1])
        else: err+=1; failures.append(res[1] if isinstance(res,tuple) else str(res))
        if i % 500 == 0:
            print(f"  fill {i}/{len(missing)} ok={ok} dup={dup} link={linkfail} err={err}", flush=True)
print(f"FILL RESULT: ok={ok} dup={dup} linkfail={linkfail} err={err}", flush=True)
if failures: print("  sample:", failures[:5], flush=True)
print("DONE fill customers")
