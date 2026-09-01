import json, sys, urllib.request, urllib.parse, http.cookiejar, os
BASE = "https://demoerpnext.s.frappe.cloud"
USR = os.environ.get("CLOUD_USR"); PWD = os.environ.get("CLOUD_PWD")
EXPORT = "C:/Users/josem/erpnext-system/pos-static/export"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def post(path, payload, csrf=None):
    path = urllib.parse.quote(path, safe="/:")
    req = urllib.request.Request(BASE+path, json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Accept","application/json")
    if csrf: req.add_header("X-Frappe-CSRF-Token", csrf)
    try:
        r = op.open(req, timeout=120); return r.status, json.loads(r.read().decode())
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

def existing_names(dt):
    names=set(); start=0
    while True:
        req = urllib.request.Request(BASE+f"/api/resource/{urllib.parse.quote(dt)}?fields=[\"name\"]&limit_start={start}&limit_page_length=1000", method="GET")
        req.add_header("Cookie", "; ".join(f"{c.name}={c.value}" for d in cj._cookies.values() for p in d.values() for c in p.values()))
        req.add_header("Accept","application/json")
        try: r=op.open(req,timeout=60); data=json.loads(r.read().decode())
        except urllib.error.HTTPError: break
        rows=data.get("data",[])
        if not rows: break
        for x in rows: names.add(x["name"])
        if len(rows)<1000: break
        start+=1000
    return names

def import_dt(dt, batch=500):
    fname = dt.replace(" ", "_")+".json"
    fp = os.path.join(EXPORT, fname)
    if not os.path.exists(fp): print("NO EXPORT", dt); return
    rows = json.load(open(fp, encoding="utf-8"))
    ex = existing_names(dt)
    print(f"{dt}: export={len(rows)} existing_on_cloud={len(ex)}")
    new = [r for r in rows if r.get("name") not in ex]
    print(f"  to_insert={len(new)}")
    inserted=0; failed=0
    for i in range(0, len(new), batch):
        chunk=new[i:i+batch]
        docs=[{**{k:v for k,v in r.items() if k not in META and not k.startswith("__")}, "doctype":dt} for r in chunk]
        s,j=post("/api/method/frappe.client.insert_many", {"docs":docs,"ignore_links":True}, csrf)
        if s==200:
            inserted+=len(docs); print(f"  batch {i}-{i+len(docs)} OK ({inserted}/{len(new)})")
        else:
            failed+=len(docs)
            print(f"  batch {i} FAIL {s}: {str(j.get('exception') or j.get('_error_message') or j)[:160]}")
            break
    print(f"DONE {dt}: inserted={inserted} failed={failed}")

if __name__=="__main__":
    dt = sys.argv[1] if len(sys.argv)>1 else "Vehicle Make"
    import_dt(dt)
