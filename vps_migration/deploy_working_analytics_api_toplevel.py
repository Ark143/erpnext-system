import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

script_code = """
company = frappe.form_dict.get('company')

# Filters
s_filt = {'docstatus': 1}
p_filt = {'docstatus': 1}
j_filt = {}

if company and company not in ('All Companies', 'all', 'All'):
    s_filt['company'] = company
    p_filt['company'] = company
    j_filt['company'] = company

# 1. Sales
invs = frappe.get_all('Sales Invoice', filters=s_filt, fields=['grand_total', 'posting_date', 'company'], limit_page_length=500)
tot_sales = 0.0
co_sales = {}
month_sales = {}

for i in invs:
    amt = float(i.get('grand_total') or 0)
    tot_sales += amt
    co = i.get('company') or 'Other'
    co_sales[co] = co_sales.get(co, 0.0) + amt
    m = str(i.get('posting_date') or '')[:7]
    if m:
        month_sales[m] = month_sales.get(m, 0.0) + amt

# 2. Purchases
pinvs = frappe.get_all('Purchase Invoice', filters=p_filt, fields=['grand_total', 'company'], limit_page_length=500)
tot_purch = 0.0
supp_purch = {}

for p in pinvs:
    amt = float(p.get('grand_total') or 0)
    tot_purch += amt
    co = p.get('company') or 'Other'
    supp_purch[co] = supp_purch.get(co, 0.0) + amt

# 3. Vehicles & Workshop
vehicles = frappe.get_all('Customer Vehicle', fields=['name', 'make', 'model'], limit_page_length=500)
tot_vehicles = len(vehicles)

veh_makes = {}
for v in vehicles:
    mk = v.get('make') or 'Other'
    veh_makes[mk] = veh_makes.get(mk, 0) + 1

jos = frappe.get_all('Vehicle Job Order', filters=j_filt, fields=['name', 'status', 'company', 'customer_name', 'customer_vehicle', 'creation'], order_by='creation desc', limit_page_length=100)
tot_jobs = len(jos)

jo_status = {}
for j in jos:
    st = j.get('status') or 'Open'
    jo_status[st] = jo_status.get(st, 0) + 1

insps = frappe.get_all('Vehicle Inspection', filters=j_filt, fields=['name'], limit_page_length=500)
tot_insps = len(insps)

# 4. Stock
bins = frappe.get_all('Bin', fields=['valuation_rate', 'actual_qty', 'warehouse'], limit_page_length=500)
tot_stock_val = 0.0
wh_stock = {}

for b in bins:
    q = float(b.get('actual_qty') or 0)
    r = float(b.get('valuation_rate') or 0)
    if q > 0:
        val = q * r
        tot_stock_val += val
        wh = b.get('warehouse') or 'Main'
        wh_stock[wh] = wh_stock.get(wh, 0.0) + val

items_all = frappe.get_all('Item', filters={'disabled': 0}, fields=['name'], limit_page_length=500)
tot_items = len(items_all)

# 5. Top Items
top_items_raw = frappe.get_all('Sales Invoice Item', filters={'docstatus': 1}, fields=['item_name', 'qty', 'amount'], limit_page_length=300)
items_agg = {}

for it in top_items_raw:
    iname = it.get('item_name') or 'Item'
    if iname not in items_agg:
        items_agg[iname] = {'qty': 0.0, 'amount': 0.0}
    items_agg[iname]['qty'] += float(it.get('qty') or 0)
    items_agg[iname]['amount'] += float(it.get('amount') or 0)

# Format structured lists
co_sales_list = []
for k in co_sales:
    co_sales_list.append({'company': k, 'total': co_sales[k]})

month_sales_list = []
for k in month_sales:
    month_sales_list.append({'month': k, 'total': month_sales[k]})

supp_list = []
for k in supp_purch:
    supp_list.append({'supplier': k, 'amount': supp_purch[k]})

wh_list = []
for k in wh_stock:
    wh_list.append({'warehouse': k, 'value': wh_stock[k]})

items_list = []
for k in items_agg:
    items_list.append({'name': k, 'qty': items_agg[k]['qty'], 'amount': items_agg[k]['amount']})

makes_list = []
for k in veh_makes:
    makes_list.append({'make': k, 'count': veh_makes[k]})

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
    'monthly_sales': month_sales_list,
    'jo_status': jo_status,
    'top_items': items_list,
    'top_suppliers': supp_list,
    'warehouse_stock': wh_list,
    'top_makes': makes_list,
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
print("Updated Server Script 'VM Get Analytics Dashboard'")

# Test the API
res = op.open(urllib.request.Request(f"{URL}/api/method/vm_get_analytics_dashboard", headers=H))
data = json.loads(res.read().decode()).get('message', {})
print("API Response Status:", data.get('status'))
print("KPIs:\n", json.dumps(data.get('kpis'), indent=2))
print("Company sales items:", len(data.get('company_sales', [])))
print("Top Items count:", len(data.get('top_items', [])))
print("Recent Ops count:", len(data.get('recent_ops', [])))
