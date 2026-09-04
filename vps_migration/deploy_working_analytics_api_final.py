import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

script_code = """
try:
    company = frappe.form_dict.get('company')
    
    # 1. Sales & Invoices
    sales_filters = {'docstatus': 1}
    purch_filters = {'docstatus': 1}
    jo_filters = {}
    
    if company and company not in ('All Companies', 'all', 'All'):
        sales_filters['company'] = company
        purch_filters['company'] = company
        jo_filters['company'] = company

    invoices = frappe.get_all('Sales Invoice', filters=sales_filters, fields=['name', 'grand_total', 'posting_date', 'company', 'customer'], limit_page_length=500)
    total_sales = 0.0
    sales_by_co = {}
    monthly_sales = {}
    
    for inv in invoices:
        amt = float(inv.get('grand_total') or 0)
        total_sales += amt
        co = inv.get('company') or 'Other'
        sales_by_co[co] = sales_by_co.get(co, 0.0) + amt
        pdate = str(inv.get('posting_date') or '')[:7]
        if pdate:
            monthly_sales[pdate] = monthly_sales.get(pdate, 0.0) + amt

    # 2. Purchases & Vendors
    pinvs = frappe.get_all('Purchase Invoice', filters=purch_filters, fields=['name', 'grand_total', 'company', 'supplier'], limit_page_length=500)
    total_purchases = 0.0
    supp_by_co = {}
    for p in pinvs:
        amt = float(p.get('grand_total') or 0)
        total_purchases += amt
        s_name = p.get('supplier') or p.get('company') or 'Other'
        supp_by_co[s_name] = supp_by_co.get(s_name, 0.0) + amt

    # 3. Fleet & Job Orders
    vehicles = frappe.get_all('Customer Vehicle', fields=['name', 'make', 'model'], limit_page_length=500)
    total_vehicles = len(vehicles)
    
    veh_makes = {}
    for v in vehicles:
        mk = v.get('make') or 'Other'
        veh_makes[mk] = veh_makes.get(mk, 0) + 1

    jos = frappe.get_all('Vehicle Job Order', filters=jo_filters, fields=['name', 'status', 'company', 'customer_name', 'customer_vehicle', 'creation'], order_by='creation desc', limit_page_length=100)
    total_job_orders = len(jos)
    
    jo_status = {}
    for j in jos:
        st = j.get('status') or 'Open'
        jo_status[st] = jo_status.get(st, 0) + 1

    inspections = frappe.get_all('Vehicle Inspection', filters=jo_filters, fields=['name'], limit_page_length=500)
    total_inspections = len(inspections)

    # 4. Stock & Inventory
    bins = frappe.get_all('Bin', fields=['valuation_rate', 'actual_qty', 'warehouse', 'item_code'], limit_page_length=500)
    total_stock_value = 0.0
    wh_stock = {}
    for b in bins:
        qty = float(b.get('actual_qty') or 0)
        rate = float(b.get('valuation_rate') or 0)
        if qty > 0:
            val = qty * rate
            total_stock_value += val
            wh = b.get('warehouse') or 'Main'
            wh_stock[wh] = wh_stock.get(wh, 0.0) + val

    items_all = frappe.get_all('Item', filters={'disabled': 0}, fields=['name'], limit_page_length=500)
    total_items = len(items_all)

    # 5. Top Selling Products
    top_items_raw = frappe.get_all('Sales Invoice Item', filters={'docstatus': 1}, fields=['item_name', 'qty', 'amount'], limit_page_length=300)
    items_agg = {}
    for it in top_items_raw:
        iname = it.get('item_name') or 'Item'
        if iname not in items_agg:
            items_agg[iname] = {'qty': 0.0, 'amount': 0.0}
        items_agg[iname]['qty'] += float(it.get('qty') or 0)
        items_agg[iname]['amount'] += float(it.get('amount') or 0)

    # Convert dicts to clean lists
    co_sales_list = []
    for k in sales_by_co:
        co_sales_list.append({'company': k, 'total': sales_by_co[k]})

    monthly_sales_list = []
    for k in monthly_sales:
        monthly_sales_list.append({'month': k, 'total': monthly_sales[k]})

    supp_list = []
    for k in supp_by_co:
        supp_list.append({'supplier': k, 'amount': supp_by_co[k]})

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
            'total_sales': total_sales,
            'total_invoices_count': len(invoices),
            'total_purchases': total_purchases,
            'total_vehicles': total_vehicles,
            'total_job_orders': total_job_orders,
            'total_inspections': total_inspections,
            'total_stock_value': total_stock_value,
            'total_items': total_items
        },
        'company_sales': co_sales_list,
        'monthly_sales': monthly_sales_list,
        'jo_status': jo_status,
        'top_items': items_list,
        'top_suppliers': supp_list,
        'warehouse_stock': wh_list,
        'top_makes': makes_list,
        'recent_ops': jos[:10]
    }
except Exception as e:
    frappe.response['message'] = {
        'status': 'error',
        'error': str(e)
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
