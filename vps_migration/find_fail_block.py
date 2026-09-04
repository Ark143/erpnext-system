import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

blocks = [
    ("Block 1 (Sales)", """
invs = frappe.get_all('Sales Invoice', filters={'docstatus': 1}, fields=['grand_total', 'posting_date', 'company'], limit_page_length=500)
tot_sales = sum([float(i.get('grand_total') or 0) for i in invs])
frappe.response['message'] = {'tot_sales': tot_sales}
"""),
    ("Block 2 (Purchases)", """
pinvs = frappe.get_all('Purchase Invoice', filters={'docstatus': 1}, fields=['grand_total', 'company'], limit_page_length=500)
tot_purch = sum([float(p.get('grand_total') or 0) for p in pinvs])
frappe.response['message'] = {'tot_purch': tot_purch}
"""),
    ("Block 3 (Vehicles)", """
vehicles = frappe.get_all('Customer Vehicle', fields=['name', 'make', 'model'], limit_page_length=500)
frappe.response['message'] = {'vehicles': len(vehicles)}
"""),
    ("Block 4 (Jobs)", """
jos = frappe.get_all('Vehicle Job Order', fields=['name', 'status', 'company', 'customer_name', 'customer_vehicle', 'creation'], order_by='creation desc', limit_page_length=100)
frappe.response['message'] = {'jobs': len(jos)}
"""),
    ("Block 5 (Bins)", """
bins = frappe.get_all('Bin', fields=['valuation_rate', 'actual_qty', 'warehouse'], limit_page_length=500)
tot_stock_val = sum([float(b.get('actual_qty') or 0) * float(b.get('valuation_rate') or 0) for b in bins if float(b.get('actual_qty') or 0) > 0])
frappe.response['message'] = {'stock': tot_stock_val}
"""),
    ("Block 6 (Items)", """
items_all = frappe.get_all('Item', filters={'disabled': 0}, fields=['name'], limit_page_length=500)
frappe.response['message'] = {'items': len(items_all)}
"""),
    ("Block 7 (Top Items)", """
top_items_raw = frappe.get_all('Sales Invoice Item', filters={'docstatus': 1}, fields=['item_name', 'qty', 'amount'], limit_page_length=300)
frappe.response['message'] = {'top_items': len(top_items_raw)}
""")
]

for label, code in blocks:
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
        print(f"[PASS] {label}: {out}")
    except Exception as e:
        print(f"[FAIL] {label}: {e}")
