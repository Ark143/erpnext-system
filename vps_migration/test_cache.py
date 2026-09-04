import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

# Let's test what happens if we patch via Server Script
script_code = """
# In Server Script, let's see what we can do with frappe
# Check if frappe.desk.notifications or get_open_count is accessible
res = {}
try:
    # Check if we can write to tabDocType Link or clear cache
    frappe.clear_cache(doctype="Vehicle Job Order")
    res['cache_cleared'] = True
except Exception as e:
    res['err'] = str(e)

frappe.response['message'] = res
"""

name = "VM Test Cache"
payload = {
    'name': name,
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_test_cache',
    'allow_guest': 0,
    'disabled': 0,
    'script': script_code
}

req = urllib.request.Request(f"{URL}/api/resource/Server%20Script/{urllib.parse.quote(name)}", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
try:
    req.get_method = lambda: 'PUT'
    op.open(req)
except Exception:
    req = urllib.request.Request(f"{URL}/api/resource/Server%20Script", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
    op.open(req)

res = op.open(urllib.request.Request(f'{URL}/api/method/vm_test_cache', headers=H))
print("Result:", res.read().decode())
