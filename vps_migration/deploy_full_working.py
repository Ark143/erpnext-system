import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

c_full = """
co = frappe.form_dict.get('company')
filt = {'docstatus': 1}
if co and co not in ('All Companies', 'all', 'All'):
    filt['company'] = co

# 1. Sales
invs = frappe.get_all('Sales Invoice', filters=filt, fields=['grand_total', 'posting_date', 'company'], limit_page_length=500)
tot_sales = sum([float(i.get('grand_total') or 0) for i in invs])

co_sales = {}
m_sales = {}
for i in invs:
    amt = float(i.get('grand_total') or 0)
    c = i.get('company') or 'Other'
    co_sales[c] = co_sales.get(c, 0.0) + amt
    m = str(i.get('posting_date') or '')[:7]
    if m:
        m_sales[m] = m_sales.get(m, 0.0) + amt

# 2. Purchases
pinvs = frappe.get_all('Purchase Invoice', filters=filt, fields=['grand_total', 'company'], limit_page_length=500)
tot_purch = sum([float(p.get('grand_total') or 0) for p in pinvs])

supp_sales = {}
for p in pinvs:
    amt = float(p.get('grand_total') or 0)
    c = p.get('company') or 'Other'
    supp_sales[c] = supp_sales.get(c, 0.0) + amt

# 3. Fleet & Jobs
vehicles = frappe.get_all('Customer Vehicle', fields=['name', 'make', 'model'], limit_page_length=500)
vmakes = {}
for v in vehicles:
    mk = v.get('make') or 'Other'
    vmakes[mk] = vmakes.get(mk, 0) + 1

jfilt = {}
if co and co not in ('All Companies', 'all', 'All'):
    jfilt['company'] = co

jos = frappe.get_all('Vehicle Job Order', filters=jfilt, fields=['name', 'status', 'company', 'customer_name', 'vehicle', 'plate_no'], limit_page_length=50)
jstats = {}
for j in jos:
    st = j.get('status') or 'Open'
    jstats[st] = jstats.get(st, 0) + 1

# 4. Inventory
bins = frappe.get_all('Bin', fields=['valuation_rate', 'actual_qty', 'warehouse'], limit_page_length=500)
tot_stock_val = sum([float(b.get('actual_qty') or 0) * float(b.get('valuation_rate') or 0) for b in bins if float(b.get('actual_qty') or 0) > 0])

wh_stock = {}
for b in bins:
    q = float(b.get('actual_qty') or 0)
    r = float(b.get('valuation_rate') or 0)
    if q > 0:
        w = b.get('warehouse') or 'Main'
        wh_stock[w] = wh_stock.get(w, 0.0) + (q * r)

# 5. Top Items
items_raw = frappe.get_all('Item', filters={'disabled': 0}, fields=['name', 'item_name', 'item_group', 'standard_rate'], limit_page_length=20)

# Build response
co_sales_list = []
for k in co_sales:
    co_sales_list.append({'company': k, 'total': co_sales[k]})

m_sales_list = []
for k in m_sales:
    m_sales_list.append({'month': k, 'total': m_sales[k]})

supp_list = []
for k in supp_sales:
    supp_list.append({'supplier': k, 'amount': supp_sales[k]})

wh_list = []
for k in wh_stock:
    wh_list.append({'warehouse': k, 'value': wh_stock[k]})

makes_list = []
for k in vmakes:
    makes_list.append({'make': k, 'count': vmakes[k]})

frappe.response['message'] = {
    'status': 'success',
    'kpis': {
        'total_sales': tot_sales,
        'total_invoices_count': len(invs),
        'total_purchases': tot_purch,
        'total_vehicles': len(vehicles),
        'total_job_orders': len(jos),
        'total_stock_value': tot_stock_val,
        'total_items': len(items_raw)
    },
    'company_sales': co_sales_list,
    'monthly_sales': m_sales_list,
    'jo_status': jstats,
    'top_items': items_raw[:8],
    'top_suppliers': supp_list[:6],
    'warehouse_stock': wh_list[:6],
    'top_makes': makes_list[:8],
    'recent_ops': jos[:8]
}
"""

payload = {
    'name': 'VM Get Analytics Dashboard',
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_get_analytics_dashboard',
    'allow_guest': 1,
    'disabled': 0,
    'script': c_full
}

req = urllib.request.Request(f"{URL}/api/resource/Server%20Script/{urllib.parse.quote('VM Get Analytics Dashboard')}", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
req.get_method = lambda: 'PUT'
op.open(req)
print("Updated Server Script 'VM Get Analytics Dashboard'")

res = op.open(urllib.request.Request(f"{URL}/api/method/vm_get_analytics_dashboard", headers=H))
out = json.loads(res.read().decode())
print("API Response:", json.dumps(out.get('message', {}).get('kpis'), indent=2))
