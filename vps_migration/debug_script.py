import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

script_code = """
import traceback
try:
    company = frappe.form_dict.get('company')
    s_filt = {'docstatus': 1}
    p_filt = {'docstatus': 1}
    j_filt = {}
    if company and company not in ('All Companies', 'all', 'All'):
        s_filt['company'] = company
        p_filt['company'] = company
        j_filt['company'] = company

    # 1. Sales
    invs = frappe.get_all('Sales Invoice', filters=s_filt, fields=['grand_total', 'posting_date', 'company'], limit_page_length=500)
    tot_sales = sum([float(i.get('grand_total') or 0) for i in invs])
    
    # 2. Purchases
    pinvs = frappe.get_all('Purchase Invoice', filters=p_filt, fields=['grand_total', 'company'], limit_page_length=500)
    tot_purch = sum([float(p.get('grand_total') or 0) for p in pinvs])

    # 3. Vehicles
    vehicles = frappe.get_all('Customer Vehicle', fields=['name', 'make', 'model'], limit_page_length=500)
    
    # 4. Jobs
    jos = frappe.get_all('Vehicle Job Order', filters=j_filt, fields=['name', 'status', 'company', 'customer_name', 'vehicle', 'plate_no'], limit_page_length=100)
    
    # 5. Stock
    bins = frappe.get_all('Bin', fields=['valuation_rate', 'actual_qty', 'warehouse'], limit_page_length=500)
    tot_stock_val = sum([float(b.get('actual_qty') or 0) * float(b.get('valuation_rate') or 0) for b in bins if float(b.get('actual_qty') or 0) > 0])

    # 6. Items
    items_all = frappe.get_all('Item', filters={'disabled': 0}, fields=['name'], limit_page_length=500)
    
    # 7. Top Items
    top_items_raw = frappe.get_all('Sales Invoice Item', filters={'docstatus': 1}, fields=['item_name', 'qty', 'amount'], limit_page_length=300)

    frappe.response['message'] = {
        'status': 'success',
        'kpis': {
            'total_sales': tot_sales,
            'total_invoices_count': len(invs),
            'total_purchases': tot_purch,
            'total_vehicles': len(vehicles),
            'total_job_orders': len(jos),
            'total_stock_value': tot_stock_val,
            'total_items': len(items_all)
        }
    }
except Exception as e:
    frappe.response['message'] = {'status': 'error', 'err': str(e)}
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
print("Updated Server Script")

res = op.open(urllib.request.Request(f"{URL}/api/method/vm_get_analytics_dashboard", headers=H))
print("Response:", res.read().decode())
