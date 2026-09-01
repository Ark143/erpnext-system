import json, urllib.request, urllib.parse, http.cookiejar, os
BASE = "https://demoerpnext.s.frappe.cloud"
USR = os.environ.get("CLOUD_USR"); PWD = os.environ.get("CLOUD_PWD")
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def post(path, payload, csrf=None):
    path = urllib.parse.quote(path, safe="/:")
    req = urllib.request.Request(BASE+path, json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Accept","application/json")
    if csrf: req.add_header("X-Frappe-CSRF-Token", csrf)
    try:
        r = op.open(req, timeout=60); return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {}
s,j = post("/api/method/login", {"usr":USR,"pwd":PWD})
csrf=None
for d in cj._cookies.values():
    for p in d.values():
        for c in p.values():
            if c.name=="csrf_token": csrf=c.value
for dt in ["Company","Customer","Supplier","Item","Vehicle Make","Vehicle Model","Customer Vehicle",
           "Item Group","Customer Group","Warehouse","Account","Cost Center","POS Profile","Mode of Payment","Price List","Bin Location","Cashier Profile","Vehicle Service Reminder","Vehicle POS Invoice"]:
    s,j = post("/api/method/frappe.client.get_count", {"doctype": dt}, csrf)
    print(f"{dt}: {j.get('message') if s==200 else 'ERR '+str(j)[:80]}")
