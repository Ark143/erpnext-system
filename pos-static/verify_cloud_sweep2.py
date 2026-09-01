import json, sys, urllib.request, urllib.parse, http.cookiejar, os
BASE = "https://demoerpnext.s.frappe.cloud"
USR = os.environ.get("CLOUD_USR"); PWD = os.environ.get("CLOUD_PWD")
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def post(path, payload, csrf=None):
    req = urllib.request.Request(BASE+path, json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Accept","application/json")
    if csrf: req.add_header("X-Frappe-CSRF-Token", csrf)
    try:
        r = op.open(req, timeout=60); return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read().decode())
        except Exception: body = {"error": e.reason}
        return e.code, body
    except Exception as e:
        return "ERR", {"error": str(e)}

def get_csrf():
    s,j = post("/api/method/login", {"usr":USR,"pwd":PWD})
    if s!=200:
        print("LOGIN FAIL", s, j.get("message") if isinstance(j,dict) else j); sys.exit(1)
    csrf=None
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": csrf=c.value
    return csrf

csrf = get_csrf()
print("login OK, csrf present:", bool(csrf))

# --- count helper: returns (status, value) ---
def count(dt):
    s,j = post("/api/method/frappe.client.get_count", {"doctype": dt}, csrf)
    if s==200: return "OK", j.get("message")
    if s==403: return "NO_PERM", "403"
    if s==404: return "MISSING", "404"
    return "ERR", f"{s}:{str(j.get('exception') or j.get('_error_message') or j.get('error'))[:80]}"

results = {}
print("\n=== CUSTOM DOCTYPES (Vehicle Management) ===")
custom = ["Vehicle Make","Vehicle Model","Customer Vehicle","Cashier Profile","Inspection Template",
          "Inspection Template Item","Item Part Cross Reference","Item Vehicle Compatibility","Bin Location",
          "Vehicle Service Reminder","Vehicle POS Invoice","Vehicle POS Invoice Item","Vehicle Inspection",
          "Vehicle Inspection Item","Job Order Part Item","Job Order Service Item","Vehicle Estimate","Vehicle Job Order"]
for dt in custom:
    st,val = count(dt)
    results[dt]= (st,val)
    print(f"  {dt}: {st} {val}")

print("\n=== BASE / STANDARD MODULES ===")
base = ["Company","Customer","Supplier","Item","Item Group","Customer Group","Supplier Group","Warehouse",
        "Account","Cost Center","POS Profile","Mode of Payment","Price List","Sales Invoice","Purchase Invoice",
        "Stock Entry","Lead","Opportunity","Quotation","Sales Order","Serial No","Batch","BOM","Work Order",
        "Purchase Order","Material Request","Payment Entry","Journal Entry","Delivery Note","Purchase Receipt",
        "Loyalty Program","Tax Category","Address","Contact","Employee","Warehouse"]
for dt in base:
    st,val = count(dt)
    print(f"  {dt}: {st} {val}")
    results[dt]=(st,val)

print("\n=== WEB PAGES (published) ===")
# get_list avoids URL-space bug
s,j = post("/api/method/frappe.client.get_list", {"doctype":"Web Page","fields":["name","title","route","published"],"filters":[["published",">",0]]}, csrf)
if s==200:
    pages = j.get("message", [])
    print(f"  published web pages: {len(pages)}")
    for p in pages:
        results["WebPage/"+str(p.get("route"))]=("OK", p.get("title"))
        print(f"    [{p.get('route')}] {p.get('title')}")
else:
    print(f"  Web Page list: {s} {str(j.get('exception') or j.get('error'))[:120]}")
    results["WebPage"]=("ERR", s)

print("\n=== SERVER SCRIPTS (enabled) ===")
s,j = post("/api/method/frappe.client.get_list", {"doctype":"Server Script","fields":["name","enabled","script_type"],"filters":[]}, csrf)
if s==200:
    ss = j.get("message", [])
    print(f"  server scripts: {len(ss)}")
    for x in ss:
        flag = "ENABLED" if x.get("enabled") else "disabled"
        print(f"    [{flag}] {x.get('name')} ({x.get('script_type')})")
        results["ServerScript/"+str(x.get("name"))]=(flag, x.get("script_type"))
else:
    print(f"  Server Script list: {s} {str(j.get('exception') or j.get('error'))[:120]}")
    results["ServerScript"]=("ERR", s)

print("\n=== POS ROUTE CHECK (read-only, via desk module link / exists?) ===")
# check if a custom Page 'vehicle_pos' exists
s,j = post("/api/method/frappe.client.get_count", {"doctype":"Page"}, csrf)
print(f"  Page doctype total: {s} {j.get('message') if s==200 else j.get('exception') or j.get('error')}")
# check whether a route /vehicle_pos or similar is reachable is browser-side; note here
results["POS_PAGE"]=("note","custom POS page only exists if app deployed (MIG-007 app deploy pending)")

print("\nDONE")
# dump JSON for the log
with open(os.path.join(os.path.dirname(__file__),"verify_cloud_sweep2.out"),"w",encoding="utf-8") as f:
    f.write(json.dumps(results, indent=2, default=str))
print("wrote verify_cloud_sweep2.out")
