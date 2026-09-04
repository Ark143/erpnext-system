import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

c1 = """
co = frappe.form_dict.get('company')
filt = {'docstatus': 1}
if co: filt['company'] = co
invs = frappe.get_all('Sales Invoice', filters=filt, fields=['grand_total', 'posting_date', 'company'], limit_page_length=200)
pinvs = frappe.get_all('Purchase Invoice', filters=filt, fields=['grand_total', 'company'], limit_page_length=200)
frappe.response['message'] = {'s': len(invs), 'p': len(pinvs)}
"""

c2 = c1 + """
vehicles = frappe.get_all('Customer Vehicle', fields=['name', 'make', 'model'], limit_page_length=200)
jfilt = {}
if co: jfilt['company'] = co
jos = frappe.get_all('Vehicle Job Order', filters=jfilt, fields=['name', 'status', 'company', 'customer_name', 'vehicle', 'plate_no'], limit_page_length=50)
frappe.response['message']['v'] = len(vehicles)
frappe.response['message']['j'] = len(jos)
"""

c3 = c2 + """
bins = frappe.get_all('Bin', fields=['valuation_rate', 'actual_qty', 'warehouse'], limit_page_length=200)
tot_stock_val = sum([float(b.get('actual_qty') or 0) * float(b.get('valuation_rate') or 0) for b in bins if float(b.get('actual_qty') or 0) > 0])
frappe.response['message']['stock'] = tot_stock_val
"""

c4 = c3 + """
co_sales = {}
m_sales = {}
for i in invs:
    amt = float(i.get('grand_total') or 0)
    c = i.get('company') or 'Other'
    co_sales[c] = co_sales.get(c, 0.0) + amt
    m = str(i.get('posting_date') or '')[:7]
    if m: m_sales[m] = m_sales.get(m, 0.0) + amt
frappe.response['message']['co_sales'] = co_sales
"""

combos = [("c1", c1), ("c2", c2), ("c3", c3), ("c4", c4)]

for lbl, code in combos:
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
        print(f"[PASS] {lbl}: {res.read().decode()}")
    except Exception as e:
        print(f"[FAIL] {lbl}: {e}")
