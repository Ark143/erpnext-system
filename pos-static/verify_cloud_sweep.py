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
def count(dt):
    s,j = post("/api/method/frappe.client.get_count", {"doctype": dt}, csrf)
    if s==200: return j.get("message")
    return f"ERR{s}"
def exists_dt(dt):
    # try get meta to confirm doctype exists/accessible
    s,j = post("/api/method/frappe.client.get_count", {"doctype": dt}, csrf)
    if s==200: return True
    if s==403: return "NO_PERM"
    if s==404: return "MISSING"
    return f"ERR{s}"

print("=== CUSTOM DOCTYPES (created on cloud) ===")
custom = ["Vehicle Make","Vehicle Model","Customer Vehicle","Cashier Profile","Inspection Template",
          "Inspection Template Item","Item Part Cross Reference","Item Vehicle Compatibility","Bin Location",
          "Vehicle Service Reminder","Vehicle POS Invoice","Vehicle POS Invoice Item","Vehicle Inspection",
          "Vehicle Inspection Item","Job Order Part Item","Job Order Service Item","Vehicle Estimate","Vehicle Job Order"]
for dt in custom:
    c = count(dt)
    print(f"  {dt}: {c}")

print("=== BASE / STANDARD MODULES ===")
for dt in ["Company","Customer","Supplier","Item","Item Group","Customer Group","Supplier Group","Warehouse",
           "Account","Cost Center","POS Profile","Mode of Payment","Price List","Sales Invoice","Purchase Invoice",
           "Stock Entry","Lead","Opportunity","Quotation","Sales Order"]:
    c = count(dt)
    print(f"  {dt}: {c}")

print("=== WEB PAGES / SERVER SCRIPTS / DESK PAGES ===")
for dt in ["Web Page","Server Script","Page","DocType","Module Def"]:
    c = count(dt)
    print(f"  {dt}: {c}")

print("=== CHECK vehicle-related web/page artifacts ===")
s,j = post("/api/resource/Web Page", {"filters":["title","like","%Vehicle%"],"fields":["name","title"]}, csrf)
print("  Web Page like Vehicle:", j.get("message") if s==200 else j)
s,j = post("/api/resource/Page", {"filters":["title","like","%vehicle%"],"fields":["name","title"]}, csrf)
print("  Page like vehicle:", j.get("message") if s==200 else j)
print("DONE")
