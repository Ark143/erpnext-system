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
    if s!=200:
        print("LOGIN FAIL", s); sys.exit(1)
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": return c.value

csrf = get_csrf()
print("login OK")

# ---- remaps for group->leaf (cloud rejects group nodes in leaf-required links) ----
REMAP = {
    "Customer": {
        "customer_group": {"All Customer Groups": "Individual", "Commercial": "Commercial", "Individual": "Individual"},
        "territory": {"All Territories": "Philippines"},
    },
    "Supplier": {
        "supplier_group": {"All Supplier Groups": "Local"},
    },
    "Item": {
        "item_group": {"GENERAL REPAIRS": "Services", "OTHER SERVICES": "Services",
                       "TRANSMISSION": "TRANSMISSION", "Products": "Products", "Services": "Services"},
    },
}
# leaf Item Groups that must exist on cloud (create if missing)
ENSURE_ITEM_GROUPS = ["TRANSMISSION"]

def ensure_item_groups():
    for g in ENSURE_ITEM_GROUPS:
        s,j = post("/api/method/frappe.client.get", {"doctype":"Item Group","name":g}, csrf)
        if s==200: 
            print("  Item Group exists:", g); continue
        # create as leaf under 'All Item Groups'
        s2,j2 = post("/api/method/frappe.client.insert",
                     {"doc":{"doctype":"Item Group","item_group_name":g,"parent_item_group":"All Item Groups","is_group":0}}, csrf)
        print(f"  create Item Group {g}:", s2, str(j2.get('exception') or j2.get('message') or '')[:80])

STRIP = ["creation","modified","modified_by","owner","idx","docstatus","lft","rgt","old_parent",
         "_comments","_assign","_user_tags","_liked_by","parent","parentfield","parenttype","name"]

def import_doc(doctype, export_file, threads=5, max_retries=6):
    recs = json.load(open(export_file, encoding="utf-8"))
    print(f"\n=== {doctype}: {len(recs)} records ===", flush=True)
    ok=dup=linkfail=perm=err=0; failures=[]
    remap = REMAP.get(doctype, {})
    def clean(r):
        doc = {}
        for k,v in r.items():
            if k in STRIP: continue
            if v is None or v=="" : continue
            if k in remap and k in doc:  # already set? skip
                pass
            doc[k]=v
        doc["doctype"]=doctype
        # apply remaps
        for fld,mp in remap.items():
            if fld in doc and doc[fld] in mp:
                doc[fld]=mp[doc[fld]]
        return doc
    def do_one(r):
        doc = clean(r)
        for attempt in range(max_retries):
            s,j = post("/api/method/frappe.client.insert", {"doc": doc}, csrf)
            if s==200: return "ok"
            if s==409: return "dup"
            if s==403: return "perm"
            if s==429:
                time.sleep(2*(attempt+1)); continue
            ex=str(j.get("exception") or j.get("_error_message") or j.get("message") or j.get("error"))
            if "LinkValidationError" in ex or "could not find" in ex.lower() or "Group type" in ex:
                return ("linkfail", ex[:200])
            if s==417 and attempt < max_retries-1:
                time.sleep(1); continue
            return ("err", f"{s} {ex[:160]}")
        return "err"
    with ThreadPoolExecutor(max_workers=threads) as ex:
        for i,res in enumerate(ex.map(do_one, recs), 1):
            if res=="ok": ok+=1
            elif res=="dup": dup+=1
            elif res=="perm": perm+=1
            elif isinstance(res,tuple) and res[0]=="linkfail": linkfail+=1; failures.append(res[1])
            else: err+=1; failures.append(res[1] if isinstance(res,tuple) else str(res))
            if i % 2000 == 0:
                print(f"  progress {i}/{len(recs)} ok={ok} dup={dup} link={linkfail} err={err}", flush=True)
            if perm>=1:
                print("  PERMISSION 403 — stopping", flush=True); break
    print(f"  RESULT {doctype}: ok={ok} dup={dup} linkfail={linkfail} perm={perm} err={err}", flush=True)
    if failures:
        print("  sample failures:", failures[:5], flush=True)
    return perm

print("\n-- ensure missing leaf groups --")
ensure_item_groups()

PLAN = [
    ("Customer", "pos-static/export/Customer.json", 6),
    ("Supplier", "pos-static/export/Supplier.json", 4),
    ("Item", "pos-static/export/Item.json", 4),
]
for dt,f,th in PLAN:
    if import_doc(dt,f,threads=th):
        print(f"STOP on 403 {dt}"); break
print("\nDONE batch (fixed)")
