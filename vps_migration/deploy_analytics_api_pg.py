import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

server_script_code = """
company = frappe.form_dict.get('company')

# Company filter
co_sql = ""
params = []
if company and company not in ("All Companies", "all", "All"):
    co_sql = ' WHERE company = %s '
    params = [company]

# 1. Total Sales & Invoice Count
sales_sql = 'SELECT COALESCE(SUM(grand_total), 0) as total_sales, COUNT(name) as count FROM "tabSales Invoice" WHERE docstatus = 1'
if co_sql:
    sales_sql += ' AND company = %s'
sales_res = frappe.db.sql(sales_sql, params if co_sql else (), as_dict=True)[0]
total_sales = float(sales_res['total_sales'] or 0)
total_invoices_count = int(sales_res['count'] or 0)

# 2. Total Purchases
purch_sql = 'SELECT COALESCE(SUM(grand_total), 0) as total_purchases, COUNT(name) as count FROM "tabPurchase Invoice" WHERE docstatus = 1'
if co_sql:
    purch_sql += ' AND company = %s'
purch_res = frappe.db.sql(purch_sql, params if co_sql else (), as_dict=True)[0]
total_purchases = float(purch_res['total_purchases'] or 0)

# 3. Fleet & Job Orders
total_vehicles = int(frappe.db.sql('SELECT COUNT(name) as c FROM "tabCustomer Vehicle"', as_dict=True)[0]['c'] or 0)

jo_sql = 'SELECT COUNT(name) as c FROM "tabVehicle Job Order"' + (co_sql if co_sql else '')
total_job_orders = int(frappe.db.sql(jo_sql, params if co_sql else (), as_dict=True)[0]['c'] or 0)

insp_sql = 'SELECT COUNT(name) as c FROM "tabVehicle Inspection"' + (co_sql if co_sql else '')
total_inspections = int(frappe.db.sql(insp_sql, params if co_sql else (), as_dict=True)[0]['c'] or 0)

# 4. Stock Value & Total Items
stock_sql = 'SELECT COALESCE(SUM(valuation_rate * actual_qty), 0) as total_val FROM "tabBin" WHERE actual_qty > 0'
stock_res = frappe.db.sql(stock_sql, as_dict=True)[0]
total_stock_value = float(stock_res['total_val'] or 0)
total_items = int(frappe.db.sql('SELECT COUNT(name) as c FROM "tabItem" WHERE disabled = 0', as_dict=True)[0]['c'] or 0)

# 5. Sales by Company (Top 6 Branches)
sales_by_co = frappe.db.sql('''
    SELECT company, COALESCE(SUM(grand_total), 0) as total, COUNT(name) as count
    FROM "tabSales Invoice"
    WHERE docstatus = 1
    GROUP BY company
    ORDER BY total DESC
    LIMIT 6
''', as_dict=True)

# 6. Monthly Sales Trends (Last 6 Months)
monthly_sales = frappe.db.sql('''
    SELECT SUBSTRING(posting_date::text, 1, 7) as month, COALESCE(SUM(grand_total), 0) as total
    FROM "tabSales Invoice"
    WHERE docstatus = 1
    GROUP BY SUBSTRING(posting_date::text, 1, 7)
    ORDER BY month ASC
    LIMIT 12
''', as_dict=True)

# 7. Job Orders by Status
jo_status_raw = frappe.db.sql('''
    SELECT status, COUNT(name) as count
    FROM "tabVehicle Job Order" ''' + (co_sql if co_sql else '') + '''
    GROUP BY status
''', params if co_sql else (), as_dict=True)
jo_status = {r['status'] or 'Open': int(r['count']) for r in jo_status_raw}

# 8. Top Selling Products / Parts
top_items = frappe.db.sql('''
    SELECT item_name as name, COALESCE(SUM(qty), 0) as qty, COALESCE(SUM(amount), 0) as amount
    FROM "tabSales Invoice Item"
    WHERE docstatus = 1
    GROUP BY item_name
    ORDER BY amount DESC
    LIMIT 6
''', as_dict=True)

# 9. Top Suppliers
top_suppliers = frappe.db.sql('''
    SELECT company as supplier, COALESCE(SUM(grand_total), 0) as amount, COUNT(name) as count
    FROM "tabPurchase Invoice"
    WHERE docstatus = 1
    GROUP BY company
    ORDER BY amount DESC
    LIMIT 6
''', as_dict=True)

# 10. Warehouse Stock Distribution
wh_stock = frappe.db.sql('''
    SELECT warehouse, COALESCE(SUM(valuation_rate * actual_qty), 0) as value, COUNT(item_code) as item_count
    FROM "tabBin"
    WHERE actual_qty > 0
    GROUP BY warehouse
    ORDER BY value DESC
    LIMIT 6
''', as_dict=True)

# 11. Live Recent Workshop Operations
recent_ops = frappe.db.sql('''
    SELECT name, customer_vehicle, customer_name, status, company, creation
    FROM "tabVehicle Job Order" ''' + (co_sql if co_sql else '') + '''
    ORDER BY creation DESC
    LIMIT 8
''', params if co_sql else (), as_dict=True)

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
    'company_sales': sales_by_co,
    'monthly_sales': monthly_sales,
    'jo_status': jo_status,
    'top_items': top_items,
    'top_suppliers': top_suppliers,
    'warehouse_stock': wh_stock,
    'recent_ops': recent_ops
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
print("Company Sales count:", len(data.get('company_sales', [])))
print("Top Items count:", len(data.get('top_items', [])))
print("Recent Ops count:", len(data.get('recent_ops', [])))
