import json, sys, urllib.request, urllib.parse, http.cookiejar, os, uuid
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
    csrf=None
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": csrf=c.value
    return csrf

csrf = get_csrf()
print("login OK")

def blk(btype, data, col=12):
    return {"id": uuid.uuid4().hex[:10], "type": btype, "data": data, "col": col}

shortcuts = [
    "Vehicle POS Invoice", "Customer Vehicle", "Vehicle Inspection", "Vehicle Job Order",
    "Vehicle Estimate", "Vehicle Make", "Vehicle Model", "Cashier Profile",
    "Inspection Template", "Item Part Cross Reference", "Item Vehicle Compatibility",
    "Bin Location", "Vehicle Service Reminder",
]
content = []
content.append(blk("header", {"text": "<span class=\"h4\"><b>Vehicle Management</b></span>"}, 12))
for name in shortcuts:
    content.append(blk("shortcut", {"shortcut_name": name, "col": 3}, 3))

doc = {
    "doctype": "Workspace",
    "name": "Vehicle Management",
    "title": "Vehicle Management",
    "module": "Vehicle Management",
    "category": None,
    "content": json.dumps(content),
    "public": 1,
    "is_default": 0,
    "for_user": "",
    "extends": None,
    "parent_workspace": None,
    "icon": "car",
}
s,j = post("/api/method/frappe.client.insert", {"doc": doc}, csrf)
print("INSERT Workspace:", s)
if s==200:
    print("  OK name=", j.get("message",{}).get("name"))
else:
    print("  FAIL:", str(j.get("exception") or j.get("_error_message") or j.get("message") or j.get("error"))[:300])
print("DONE")
