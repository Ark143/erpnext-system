import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

script_code = """
try:
    invoices = frappe.get_all('Sales Invoice', filters={'docstatus': 1}, fields=['grand_total', 'company'])
    tot = sum([float(i.get('grand_total') or 0) for i in invoices])
    frappe.response['message'] = {'tot': tot, 'count': len(invoices)}
except Exception as e:
    frappe.response['message'] = {'err': str(e)}
"""

payload = {
    'name': 'VM Get Analytics Dashboard',
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_get_analytics_dashboard',
    'allow_guest': 1,
    'disabled': 0,
    'script': script_code
}

req = urllib.request.Request(f"{URL}/api/resource/Server%20Script/{urllib.parse.quote('VM Get Analytics Dashboard')}", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
req.get_method = lambda: 'PUT'
op.open(req)

res = op.open(urllib.request.Request(f"{URL}/api/method/vm_get_analytics_dashboard", headers=H))
print("Probe output:", res.read().decode())
