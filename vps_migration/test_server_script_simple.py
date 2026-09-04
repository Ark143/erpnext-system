import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

script = """
# Test what we have in frappe
res = {}
res['has_write_file'] = hasattr(frappe, 'write_file')
res['has_get_module_path'] = hasattr(frappe, 'get_module_path')
res['has_get_app_path'] = hasattr(frappe, 'get_app_path')

frappe.response['message'] = res
"""

payload = {
    'name': 'VM Test Simple',
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_test_simple',
    'allow_guest': 0,
    'disabled': 0,
    'script': script
}

req = urllib.request.Request(f"{URL}/api/resource/Server%20Script/{urllib.parse.quote('VM Test Simple')}", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
req.get_method = lambda: 'PUT'
op.open(req)

res = op.open(urllib.request.Request(f'{URL}/api/method/vm_test_simple', headers=H))
print("Result:", res.read().decode())
