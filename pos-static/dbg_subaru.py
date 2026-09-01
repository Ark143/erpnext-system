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
    try: r = op.open(req, timeout=60); return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e: return e.code, {}
s,j = post("/api/method/login", {"usr":USR,"pwd":PWD})
csrf=None
for d in cj._cookies.values():
    for p in d.values():
        for c in p.values():
            if c.name=="csrf_token": csrf=c.value
cookies = "; ".join(f"{c.name}={c.value}" for d in cj._cookies.values() for p in d.values() for c in p.values())
# try fetch Subaru directly
for nm in ["Subaru","Toyota","Mitsubishi"]:
    try:
        req = urllib.request.Request(BASE+"/api/resource/Vehicle%20Make/"+urllib.parse.quote(nm), method="GET")
        req.add_header("Cookie", cookies); req.add_header("Accept","application/json")
        r=op.open(req,timeout=30); print(nm, "->", r.status, "name=", json.loads(r.read().decode()).get("data",{}).get("name"))
    except urllib.error.HTTPError as e:
        print(nm, "-> HTTP", e.code)
# also test get_list with ignore_permissions param
try:
    req = urllib.request.Request(BASE+"/api/resource/Vehicle%20Make?fields=[\"name\"]&limit_page_length=200&ignore_permissions=1", method="GET")
    req.add_header("Cookie", cookies); req.add_header("Accept","application/json")
    r=op.open(req,timeout=30); print("get_list ignore_permissions count:", len(json.loads(r.read().decode()).get("data",[])))
except urllib.error.HTTPError as e:
    print("get_list err", e.code)
