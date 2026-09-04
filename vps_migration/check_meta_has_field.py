import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

script = """
res = {}
meta = frappe.get_meta('Customer')
res['has_field_customer'] = bool(meta.has_field('customer'))
res['has_field_customer_name'] = bool(meta.has_field('customer_name'))
res['has_field_custom_vehicle_job_order'] = bool(meta.has_field('custom_vehicle_job_order'))

frappe.response['message'] = res
"""

name = "VM Check Meta HasField"
payload = {
    'name': name,
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_check_meta_has_field',
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

res = op.open(urllib.request.Request(f'{URL}/api/method/vm_check_meta_has_field', headers=H))
print("Meta check:", res.read().decode())
