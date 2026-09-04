import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

script = """
res = {}
cfields = frappe.db.sql("SELECT name, dt, fieldname, label, fieldtype FROM `tabCustom Field` WHERE dt='Customer'", as_dict=True)
dfields = frappe.db.sql("SELECT name, parent, fieldname, label, fieldtype FROM `tabDocField` WHERE parent='Customer' AND fieldname LIKE '%cust%'", as_dict=True)
res['custom_fields'] = cfields
res['docfields'] = dfields
frappe.response['message'] = res
"""

name = "VM Check Customer Fields"
payload = {
    'name': name,
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_check_customer_fields',
    'allow_guest': 0,
    'disabled': 0,
    'script': script
}

req = urllib.request.Request(f"{URL}/api/resource/Server%20Script/{urllib.parse.quote(name)}", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
try:
    req.get_method = lambda: 'PUT'
    op.open(req)
except Exception:
    req = urllib.request.Request(f"{URL}/api/resource/Server%20Script", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
    op.open(req)

res = op.open(urllib.request.Request(f'{URL}/api/method/vm_check_customer_fields', headers=H))
print("Customer fields in DB:", json.dumps(json.loads(res.read().decode())['message'], indent=2))
