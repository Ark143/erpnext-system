import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

script = """
def fix_spaces():
    frappe.db.set_value("Customer Vehicle", "0301 650263", "customer", "JOAN CHIIETE")
    frappe.db.set_value("Customer Vehicle", "0301 650263", "customer_name", "JOAN CHIIETE")
    frappe.db.commit()
    frappe.response["message"] = {"fixed": True}

fix_spaces()
"""

name = 'VM Fix Single Vehicle'
payload = {'name': name, 'doctype': 'Server Script', 'script_type': 'API', 'api_method': 'vm_fix_single_vehicle', 'allow_guest': 1, 'disabled': 0, 'script': script}
try:
    req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Server%20Script', data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
    op.open(req)
except Exception:
    req = urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Server%20Script/{urllib.parse.quote(name)}', data=urllib.parse.urlencode({'data': json.dumps({'script': script})}).encode(), headers=H)
    req.get_method = lambda: 'PUT'
    op.open(req)

r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_fix_single_vehicle', headers=H))
print('Result:', r.read().decode())
