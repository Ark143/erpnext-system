import json, urllib.request, urllib.parse, http.cookiejar, os
BASE = "https://demoerpnext.s.frappe.cloud"
USR = os.environ.get("CLOUD_USR"); PWD = os.environ.get("CLOUD_PWD")
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def post(path, payload, csrf=None):
    path = urllib.parse.quote(path, safe="/: ")
    req = urllib.request.Request(BASE+path, json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Accept","application/json")
    if csrf: req.add_header("X-Frappe-CSRF-Token", csrf)
    try: r = op.open(req, timeout=60); return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e: return e.code, {}
s,j = post("/api/method/login", {"usr":USR,"pwd":PWD})
csrf=None
for d in cj._cookies.values():
    for p in d.values():
        for c in p.values():
            if c.name=="csrf_token": csrf=c.value
cookies="; ".join(f"{c.name}={c.value}" for d in cj._cookies.values() for p in d.values() for c in p.values())
def getlist(dt, fields):
    req=urllib.request.Request(BASE+f"/api/resource/{dt}?fields={urllib.parse.quote(json.dumps(fields))}&limit_page_length=200", method="GET")
    req.add_header("Cookie",cookies); req.add_header("Accept","application/json")
    try: r=op.open(req,timeout=30); return [x.get(fields[0]) for x in json.loads(r.read().decode()).get("data",[])]
    except urllib.error.HTTPError as e: return f"ERR{e.code}"
print("Companies:", getlist("Company",["name"]))
print("Vehicle Make count:", post("/api/method/frappe.client.get_count",{"doctype":"Vehicle Make"},csrf)[1].get("message"))
print("Vehicle Model count:", post("/api/method/frappe.client.get_count",{"doctype":"Vehicle Model"},csrf)[1].get("message"))
