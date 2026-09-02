import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

script_batch = """
def batch_clean_vehicles():
    # Find vehicles where customer has extra spaces
    vehs = frappe.get_all(
        "Customer Vehicle",
        filters={"customer": ["like", "%  %"]},
        fields=["name", "customer"]
    )
    
    fixed = 0
    for v in vehs:
        raw = v.get("customer") or ""
        clean = " ".join(raw.split())
        if frappe.db.exists("Customer", clean):
            frappe.db.set_value("Customer Vehicle", v.name, "customer", clean)
            frappe.db.set_value("Customer Vehicle", v.name, "customer_name", clean)
            fixed += 1
            
    frappe.db.commit()
    frappe.response["message"] = {"found": len(vehs), "fixed": fixed}

batch_clean_vehicles()
"""

name = 'VM Batch Clean Vehicles'
payload = {'name': name, 'doctype': 'Server Script', 'script_type': 'API', 'api_method': 'vm_batch_clean_vehicles', 'allow_guest': 1, 'disabled': 0, 'script': script_batch}
try:
    req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Server%20Script', data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
    op.open(req)
except Exception:
    req = urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Server%20Script/{urllib.parse.quote(name)}', data=urllib.parse.urlencode({'data': json.dumps({'script': script_batch})}).encode(), headers=H)
    req.get_method = lambda: 'PUT'
    op.open(req)

r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_batch_clean_vehicles', headers=H))
print('Batch Clean Result:', r.read().decode())
