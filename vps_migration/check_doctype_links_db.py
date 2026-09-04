import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

script = """
links = frappe.db.sql("SELECT * FROM `tabDocType Link` WHERE parent='Vehicle Job Order'", as_dict=True)
frappe.response['message'] = {'links': links}
"""

name = "VM Check DocType Links"
payload = {
    'name': name,
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_check_doctype_links',
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

res = op.open(urllib.request.Request(f'{URL}/api/method/vm_check_doctype_links', headers=H))
print("DocType Links in DB:", json.loads(res.read().decode())['message'])
