import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

server_script_code = """
company = frappe.form_dict.get('company')
filters_sinv = {"docstatus": 1}
filters_pinv = {"docstatus": 1}
filters_jo = {}

if company and company != "All Companies" and company != "all":
    filters_sinv["company"] = company
    filters_pinv["company"] = company
    filters_jo["company"] = company

# 1. Sales & Invoices
total_sales = 0.0
invoices = frappe.get_all("Sales Invoice", filters=filters_sinv, fields=["grand_total", "posting_date", "company"])
sales_by_company = {}
for inv in invoices:
    amt = float(inv.get("grand_total") or 0)
    total_sales += amt
    co = inv.get("company") or "Other"
    sales_by_company[co] = sales_by_company.get(co, 0.0) + amt
total_invoices_count = len(invoices)

# 2. Purchases & Vendors
total_purchases = 0.0
pinvs = frappe.get_all("Purchase Invoice", filters=filters_pinv, fields=["grand_total", "company"])
supp_by_company = {}
for p in pinvs:
    amt = float(p.get("grand_total") or 0)
    total_purchases += amt
    co = p.get("company") or "Other"
    supp_by_company[co] = supp_by_company.get(co, 0.0) + amt

# 3. Fleet & Workshop
vehicles = frappe.get_all("Customer Vehicle", fields=["name", "make", "model"])
total_vehicles = len(vehicles)

jos = frappe.get_all("Vehicle Job Order", filters=filters_jo, fields=["name", "status", "company", "customer_name", "customer_vehicle", "creation"])
total_job_orders = len(jos)

jo_status_counts = {}
for j in jos:
    st = j.get("status") or "Open"
    jo_status_counts[st] = jo_status_counts.get(st, 0) + 1

inspections = frappe.get_all("Vehicle Inspection", filters=filters_jo, fields=["name"])
total_inspections = len(inspections)

# 4. Stock & Bins
bins = frappe.get_all("Bin", fields=["valuation_rate", "actual_qty", "warehouse"], limit_page_length=500)
total_stock_value = 0.0
wh_stock = {}
for b in bins:
    qty = float(b.get("actual_qty") or 0)
    rate = float(b.get("valuation_rate") or 0)
    if qty > 0:
        val = qty * rate
        total_stock_value += val
        wh = b.get("warehouse") or "Main"
        wh_stock[wh] = wh_stock.get(wh, 0.0) + val

items_all = frappe.get_all("Item", filters={"disabled": 0}, fields=["name"])
total_items = len(items_all)

# 5. Top Selling Items
top_items_raw = frappe.get_all("Sales Invoice Item", filters={"docstatus": 1}, fields=["item_name", "qty", "amount"], limit_page_length=200)
items_agg = {}
for it in top_items_raw:
    iname = it.get("item_name") or "Item"
    if iname not in items_agg:
        items_agg[iname] = {"qty": 0.0, "amount": 0.0}
    items_agg[iname]["qty"] += float(it.get("qty") or 0)
    items_agg[iname]["amount"] += float(it.get("amount") or 0)

# Format structured lists
company_sales_list = []
for k, v in sales_by_company.items():
    company_sales_list.append({"company": k, "total": v})

top_supp_list = []
for k, v in supp_by_company.items():
    top_supp_list.append({"supplier": k, "amount": v})

wh_stock_list = []
for k, v in wh_stock.items():
    wh_stock_list.append({"warehouse": k, "value": v})

top_items_list = []
for k, v in items_agg.items():
    top_items_list.append({"name": k, "qty": v["qty"], "amount": v["amount"]})

frappe.response['message'] = {
    'status': 'success',
    'kpis': {
        'total_sales': total_sales,
        'total_invoices_count': total_invoices_count,
        'total_purchases': total_purchases,
        'total_vehicles': total_vehicles,
        'total_job_orders': total_job_orders,
        'total_inspections': total_inspections,
        'total_stock_value': total_stock_value,
        'total_items': total_items
    },
    'company_sales': company_sales_list,
    'jo_status': jo_status_counts,
    'top_items': top_items_list,
    'top_suppliers': top_supp_list,
    'warehouse_stock': wh_stock_list,
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
    'script': server_script_code
}

req = urllib.request.Request(f"{URL}/api/resource/Server%20Script/{urllib.parse.quote('VM Get Analytics Dashboard')}", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
req.get_method = lambda: 'PUT'
op.open(req)
print("Updated Server Script 'VM Get Analytics Dashboard'")

# Test the API
res = op.open(urllib.request.Request(f"{URL}/api/method/vm_get_analytics_dashboard", headers=H))
data = json.loads(res.read().decode()).get('message', {})
print("API Response KPIs:")
print(json.dumps(data.get('kpis'), indent=2))
