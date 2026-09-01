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
    s,j = post("/api/method/login", {"usr":USR,"pwd":PWD}); 
    csrf=None
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": csrf=c.value
    return csrf
csrf = get_csrf()

META = ["creation","modified","modified_by","owner","idx","docstatus","amended_from","__islocal",
        "__unsaved","_comments","_assign","_user_tags","_liked_by","parent","parentfield","parenttype",
        "_last_updated","__version","lft","rgt","_user","_liked_by"]

def import_dt(dt, limit=None, batch=500):
    fname = dt.replace(" ", "_") + ".json"
    rows = json.load(open(os.path.join(EXPORT, fname), encoding="utf-8"))
    if limit: rows = rows[:limit]
    total = len(rows)
    inserted = 0; failed = 0
    for i in range(0, total, batch):
        chunk = rows[i:i+batch]
        docs = []
        for r in chunk:
            d = {k:v for k,v in r.items() if k not in META and not k.startswith("__")}
            d["doctype"] = dt
            docs.append(d)
        s,j = post("/api/method/frappe.client.insert_many", {"docs": docs, "ignore_links": True}, csrf)
        if s == 200:
            inserted += len(docs)
            print(f"  {dt}: batch {i}-{i+len(docs)} OK ({inserted}/{total})")
        else:
            failed += len(docs)
            msg = j.get("exception") or j.get("_error_message") or j.get("message") or j
            print(f"  {dt}: batch {i} FAIL {s}: {str(msg)[:200]}")
            break
    print(f"DONE {dt}: inserted={inserted} failed={failed}")
    return inserted, failed

if __name__ == "__main__":
    # smoke test
    import_dt("Vehicle Make", limit=71)
    import_dt("Customer Vehicle", limit=100)
