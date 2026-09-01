import json, sys, urllib.request, urllib.parse, http.cookiejar, os, threading
BASE = "https://demoerpnext.s.frappe.cloud"
USR = os.environ.get("CLOUD_USR"); PWD = os.environ.get("CLOUD_PWD")
EXPORT = "C:/Users/josem/erpnext-system/pos-static/export"
lock = threading.Lock()
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def post(path, payload, csrf=None):
    path = urllib.parse.quote(path, safe="/: ")
    req = urllib.request.Request(BASE+path, json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Accept","application/json")
    if csrf: req.add_header("X-Frappe-CSRF-Token", csrf)
    try: r = op.open(req, timeout=120); return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read().decode())
        except Exception: body = {"error": e.reason}
        return e.code, body
def get_csrf():
    s,j = post("/api/method/login", {"usr":USR,"pwd":PWD}); csrf=None
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": csrf=c.value
    return csrf
csrf = get_csrf()
META = ["creation","modified","modified_by","owner","idx","docstatus","amended_from","__islocal",
        "__unsaved","_comments","_assign","_user_tags","_liked_by","parent","parentfield","parenttype",
        "_last_updated","__version","lft","rgt"]
def clean(r, dt):
    return {**{k:v for k,v in r.items() if k not in META and not k.startswith("__")}, "doctype":dt}

def import_dt(dt, threads=8, limit=None):
    fname = dt.replace(" ", "_")+".json"
    fp = os.path.join(EXPORT, fname)
    if not os.path.exists(fp): print("NO EXPORT", dt); return
    rows = json.load(open(fp, encoding="utf-8"))
    if limit: rows = rows[:limit]
    print(f"{dt}: export={len(rows)}")
    ok=0; skip=0; fail=0; fails=[]
    def worker(r):
        nonlocal ok,skip,fail
        doc=clean(r,dt)
        s,j=post("/api/method/frappe.client.insert", {"doc": doc}, csrf)
        with lock:
            if s==200: ok+=1
            elif s in (409,400) and ("Duplicate" in str(j) or "exists" in str(j).lower()): skip+=1
            else:
                fail+=1
                if len(fails)<5: fails.append((r.get("name"), s, str(j.get("exception") or j.get("_error_message") or j)[:150]))
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=threads) as ex:
        list(ex.map(worker, rows))
    print(f"DONE {dt}: ok={ok} skip={skip} fail={fail}")
    for f in fails: print("  FAIL", f)

if __name__=="__main__":
    dt = sys.argv[1] if len(sys.argv)>1 else "Vehicle Make"
    lim = int(sys.argv[2]) if len(sys.argv)>2 else None
    import_dt(dt, limit=lim)
