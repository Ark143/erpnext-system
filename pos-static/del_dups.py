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
print("login OK (delete duplicates)", flush=True)

dup_names = json.load(open("pos-static/export/dup_names.txt", encoding="utf-8"))
print(f"duplicate names to delete: {len(dup_names)}", flush=True)

ok=fail=perm=0; failures=[]
def do_one(name):
    for attempt in range(6):
        s,j = post("/api/method/frappe.client.delete", {"doctype":"Customer","name":name}, csrf)
        if s==200: return "ok"
        if s==404: return "gone"   # already deleted
        if s==403: return "perm"
        if s==429: time.sleep(2*(attempt+1)); continue
        ex=str(j.get("exception") or j.get("_error_message") or j.get("message") or j.get("error"))
        if "Linked" in ex or "link" in ex.lower():
            return ("link", ex[:120])
        if s in ("ERR",417) and attempt < 5:
            time.sleep(2); continue
        return ("fail", f"{s} {ex[:120]}")
    return "fail"

with ThreadPoolExecutor(max_workers=10) as ex:
    for i,res in enumerate(ex.map(do_one, dup_names), 1):
        if res=="ok": ok+=1
        elif res=="gone": ok+=1
        elif res=="perm": perm+=1
        elif isinstance(res,tuple) and res[0]=="link": fail+=1; failures.append(res[1])
        else: fail+=1; failures.append(res[1] if isinstance(res,tuple) else str(res))
        if i % 2000 == 0:
            print(f"  progress {i}/{len(dup_names)} ok={ok} fail={fail} perm={perm}", flush=True)
        if perm>=1:
            print("  PERMISSION 403 — stopping", flush=True); break
print(f"DELETE RESULT: ok={ok} fail={fail} perm={perm}", flush=True)
if failures: print("  sample failures:", failures[:5], flush=True)
print("DONE delete duplicates")
