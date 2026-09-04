import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

blocks = [
    ("1. Sales + Monthly", """
co = frappe.form_dict.get('company')
filt = {'docstatus': 1}
if co: filt['company'] = co
invs = frappe.get_all('Sales Invoice', filters=filt, fields=['grand_total', 'posting_date', 'company'], limit_page_length=500)
co_sales = {}
m_sales = {}
for i in invs:
    amt = float(i.get('grand_total') or 0)
    c = i.get('company') or 'Other'
    co_sales[c] = co_sales.get(c, 0.0) + amt
    m = str(i.get('posting_date') or '')[:7]
    if m: m_sales[m] = m_sales.get(m, 0.0) + amt
frappe.response['message'] = {'co_sales': co_sales, 'm_sales': m_sales}
"""),
    ("2. Purchases", """
co = frappe.form_dict.get('company')
pfilt = {'docstatus': 1}
if co: pfilt['company'] = co
pinvs = frappe.get_all('Purchase Invoice', filters=pfilt, fields=['grand_total', 'company'], limit_page_length=500)
supp_sales = {}
for p in pinvs:
    amt = float(p.get('grand_total') or 0)
    c = p.get('company') or 'Other'
    supp_sales[c] = supp_sales.get(c, 0.0) + amt
frappe.response['message'] = {'supp_sales': supp_sales}
"""),
    ("3. Vehicles + Makes", """
vehicles = frappe.get_all('Customer Vehicle', fields=['name', 'make', 'model'], limit_page_length=500)
vmakes = {}
for v in vehicles:
    mk = v.get('make') or 'Other'
    vmakes[mk] = vmakes.get(mk, 0) + 1
frappe.response['message'] = {'makes': vmakes}
"""),
    ("4. Job Orders + Status", """
co = frappe.form_dict.get('company')
jfilt = {}
if co: jfilt['company'] = co
jos = frappe.get_all('Vehicle Job Order', filters=jfilt, fields=['name', 'status', 'company', 'customer_name', 'vehicle', 'plate_no'], limit_page_length=50)
jstats = {}
for j in jos:
    st = j.get('status') or 'Open'
    jstats[st] = jstats.get(st, 0) + 1
frappe.response['message'] = {'jstats': jstats, 'jos': len(jos)}
"""),
    ("5. Bins + Warehouse Stock", """
bins = frappe.get_all('Bin', fields=['valuation_rate', 'actual_qty', 'warehouse'], limit_page_length=500)
wh_stock = {}
for b in bins:
    q = float(b.get('actual_qty') or 0)
    r = float(b.get('valuation_rate') or 0)
    if q > 0:
        w = b.get('warehouse') or 'Main'
        wh_stock[w] = wh_stock.get(w, 0.0) + (q * r)
frappe.response['message'] = {'wh_stock': wh_stock}
"""),
    ("6. Top Items", """
top_items_raw = frappe.get_all('Sales Invoice Item', filters={'docstatus': 1}, fields=['item_name', 'qty', 'amount'], limit_page_length=300)
items_agg = {}
for it in top_items_raw:
    iname = it.get('item_name') or 'Item'
    if iname not in items_agg:
        items_agg[iname] = {'qty': 0.0, 'amount': 0.0}
    items_agg[iname]['qty'] += float(it.get('qty') or 0)
    items_agg[iname]['amount'] += float(it.get('amount') or 0)
frappe.response['message'] = {'items_agg': len(items_agg)}
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
        res = op.open(urllib.request.Request(f"{URL}/api/method/vm_get_analytics_dashboard?company=Ultra+MRF+Dau+Main", headers=H))
        out = json.loads(res.read().decode())
        print(f"[PASS] {label}: {out}")
    except Exception as e:
        print(f"[FAIL] {label}: {e}")
