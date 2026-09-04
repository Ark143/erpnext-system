import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

script_code = """
co = frappe.form_dict.get('company')
s_filt = {'docstatus': 1}
p_filt = {'docstatus': 1}
j_filt = {}

if co and co not in ('All Companies', 'all', 'All'):
    s_filt['company'] = co
    p_filt['company'] = co
    j_filt['company'] = co

# 1. Sales & Revenue
invs = frappe.get_all('Sales Invoice', filters=s_filt, fields=['grand_total', 'posting_date', 'company'], limit_page_length=500)
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

# 2. Purchases & Procurement
pinvs = frappe.get_all('Purchase Invoice', filters=p_filt, fields=['grand_total', 'company'], limit_page_length=500)
tot_purch = sum([float(p.get('grand_total') or 0) for p in pinvs])

supp_sales = {}
for p in pinvs:
    amt = float(p.get('grand_total') or 0)
    c = p.get('company') or 'Other'
    supp_sales[c] = supp_sales.get(c, 0.0) + amt

# 3. Vehicles & Fleet
vehicles = frappe.get_all('Customer Vehicle', fields=['name', 'make', 'model'], limit_page_length=500)
tot_vehicles = len(vehicles)
vmakes = {}
for v in vehicles:
    mk = v.get('make') or 'Other'
    vmakes[mk] = vmakes.get(mk, 0) + 1

# 4. Workshop Job Orders & Inspections
jos = frappe.get_all('Vehicle Job Order', filters=j_filt, fields=['name', 'status', 'company', 'customer_name', 'vehicle', 'plate_no'], limit_page_length=50)
tot_jobs = len(jos)
jstats = {}
for j in jos:
    st = j.get('status') or 'Open'
    jstats[st] = jstats.get(st, 0) + 1

insps = frappe.get_all('Vehicle Inspection', filters=j_filt, fields=['name'], limit_page_length=500)
tot_insps = len(insps)

# 5. Inventory & Bins
bins = frappe.get_all('Bin', fields=['valuation_rate', 'actual_qty', 'warehouse'], limit_page_length=500)
tot_stock_val = sum([float(b.get('actual_qty') or 0) * float(b.get('valuation_rate') or 0) for b in bins if float(b.get('actual_qty') or 0) > 0])

wh_stock = {}
for b in bins:
    q = float(b.get('actual_qty') or 0)
    r = float(b.get('valuation_rate') or 0)
    if q > 0:
        w = b.get('warehouse') or 'Main'
        wh_stock[w] = wh_stock.get(w, 0.0) + (q * r)

items_all = frappe.get_all('Item', filters={'disabled': 0}, fields=['name'], limit_page_length=500)
tot_items = len(items_all)

# 6. Top Items
top_items_raw = frappe.get_all('Sales Invoice Item', filters={'parenttype': 'Sales Invoice'}, fields=['item_name', 'qty', 'amount'], limit_page_length=200)
items_agg = {}
for it in top_items_raw:
    iname = it.get('item_name') or 'Item'
    if iname not in items_agg:
        items_agg[iname] = {'qty': 0.0, 'amount': 0.0}
    items_agg[iname]['qty'] += float(it.get('qty') or 0)
    items_agg[iname]['amount'] += float(it.get('amount') or 0)

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

items_list = []
for k in items_agg:
    items_list.append({'name': k, 'qty': items_agg[k]['qty'], 'amount': items_agg[k]['amount']})

makes_list = []
for k in vmakes:
    makes_list.append({'make': k, 'count': vmakes[k]})

frappe.response['message'] = {
    'status': 'success',
    'kpis': {
        'total_sales': tot_sales,
        'total_invoices_count': len(invs),
        'total_purchases': tot_purch,
        'total_vehicles': tot_vehicles,
        'total_job_orders': tot_jobs,
        'total_inspections': tot_insps,
        'total_stock_value': tot_stock_val,
        'total_items': tot_items
    },
    'company_sales': co_sales_list,
    'monthly_sales': m_sales_list,
    'jo_status': jstats,
    'top_items': items_list[:8],
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
    'script': script_code
}

req = urllib.request.Request(f"{URL}/api/resource/Server%20Script/{urllib.parse.quote('VM Get Analytics Dashboard')}", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
req.get_method = lambda: 'PUT'
op.open(req)
print("Updated Server Script 'VM Get Analytics Dashboard' successfully!")

# Test without filter
res1 = op.open(urllib.request.Request(f"{URL}/api/method/vm_get_analytics_dashboard", headers=H))
out1 = json.loads(res1.read().decode())
print("Test 1 (All Companies) KPIs:\n", json.dumps(out1.get('message', {}).get('kpis'), indent=2))

# Test with company filter
res2 = op.open(urllib.request.Request(f"{URL}/api/method/vm_get_analytics_dashboard?company=Ultra+MRF+Dau+Main", headers=H))
out2 = json.loads(res2.read().decode())
print("Test 2 (Ultra MRF Dau Main) KPIs:\n", json.dumps(out2.get('message', {}).get('kpis'), indent=2))
