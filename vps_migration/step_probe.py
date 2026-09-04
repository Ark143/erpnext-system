import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

sections = [
    ("Step 1: Sales", "invoices = frappe.get_all('Sales Invoice', filters={'docstatus': 1}, fields=['grand_total'])\nfrappe.response['message'] = {'count': len(invoices)}"),
    ("Step 2: Purchases", "pinvs = frappe.get_all('Purchase Invoice', filters={'docstatus': 1}, fields=['grand_total'])\nfrappe.response['message'] = {'count': len(pinvs)}"),
    ("Step 3: Vehicles", "vehicles = frappe.get_all('Customer Vehicle', fields=['name'])\nfrappe.response['message'] = {'count': len(vehicles)}"),
    ("Step 4: Job Orders", "jos = frappe.get_all('Vehicle Job Order', fields=['name'])\nfrappe.response['message'] = {'count': len(jos)}"),
    ("Step 5: Inspections", "insps = frappe.get_all('Vehicle Inspection', fields=['name'])\nfrappe.response['message'] = {'count': len(insps)}"),
    ("Step 6: Bins", "bins = frappe.get_all('Bin', fields=['valuation_rate', 'actual_qty'], limit_page_length=200)\nfrappe.response['message'] = {'count': len(bins)}"),
    ("Step 7: Sales Items", "items = frappe.get_all('Sales Invoice Item', filters={'docstatus': 1}, fields=['item_name', 'qty', 'amount'], limit_page_length=200)\nfrappe.response['message'] = {'count': len(items)}")
]

for name, code in sections:
    payload = {
        'name': 'VM Get Analytics Dashboard',
        'doctype': 'Server Script',
        'script_type': 'API',
        'api_method': 'vm_get_analytics_dashboard',
        'allow_guest': 1,
        'disabled': 0,
        'script': code
    }
    req = urllib.request.Request(f"{URL}/api/resource/Server%20Script/{urllib.parse.quote('VM Get Analytics Dashboard')}", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
    req.get_method = lambda: 'PUT'
    op.open(req)
    
    try:
        res = op.open(urllib.request.Request(f"{URL}/api/method/vm_get_analytics_dashboard", headers=H))
        out = json.loads(res.read().decode())
        print(f"[PASS] {name}: OK -> {out}")
    except Exception as e:
        print(f"[FAIL] {name}: FAILED -> {e}")
