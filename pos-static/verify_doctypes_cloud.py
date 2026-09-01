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
# login
s,j = post("/api/method/login", {"usr":USR,"pwd":PWD})
names = ["Vehicle Make","Vehicle Model","Customer Vehicle","Cashier Profile","Inspection Template",
 "Inspection Template Item","Item Part Cross Reference","Item Vehicle Compatibility","Bin Location",
 "Vehicle Service Reminder","Vehicle POS Invoice Item","Vehicle POS Invoice","Vehicle Inspection Item",
 "Vehicle Inspection","Job Order Part Item","Job Order Service Item","Vehicle Estimate","Vehicle Job Order"]
for n in names:
    r = post("/api/resource/DocType/%s" % urllib.parse.quote(n), {}, None)
    # GET via resource
    try:
        req = urllib.request.Request(BASE+"/api/resource/DocType/"+urllib.parse.quote(n), method="GET")
        req.add_header("Cookie", "; ".join(f"{c.name}={c.value}" for d in cj._cookies.values() for p in d.values() for c in p.values()))
        rr = op.open(req, timeout=30)
        print("EXISTS", n, rr.status)
    except urllib.error.HTTPError as e:
        print("MISSING", n, e.code)
