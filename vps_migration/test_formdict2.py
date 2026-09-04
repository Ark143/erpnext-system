import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

script_code = """
company = frappe.form_dict.company if 'company' in frappe.form_dict else None
invoices = frappe.get_all('Sales Invoice', filters={'docstatus': 1}, fields=['grand_total', 'company'], limit_page_length=500)
tot_sales = sum([float(i.get('grand_total') or 0) for i in invoices])
frappe.response['message'] = {'status': 'success', 'tot_sales': tot_sales, 'count': len(invoices), 'company': company}
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

res = op.open(urllib.request.Request(f"{URL}/api/method/vm_get_analytics_dashboard?company=Ultra+MRF+Dau+Main", headers=H))
print("Result with company param:", res.read().decode())
