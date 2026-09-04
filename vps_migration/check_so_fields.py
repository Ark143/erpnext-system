import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=15)

script_code = """
meta = frappe.get_meta('Sales Order')
has_field = meta.has_field('sales_invoice')
docfield_rows = frappe.db.sql('SELECT name, fieldname, fieldtype FROM `tabDocField` WHERE parent = \\'Sales Order\\' AND fieldname = \\'sales_invoice\\'', as_dict=True)
custom_field_rows = frappe.db.sql('SELECT name, fieldname, fieldtype FROM `tabCustom Field` WHERE dt = \\'Sales Order\\' AND fieldname = \\'sales_invoice\\'', as_dict=True)
so_columns = frappe.db.sql('SELECT column_name FROM information_schema.columns WHERE table_name = \\'tabSales Order\\'', as_dict=True)
col_names = [c['column_name'] for c in so_columns]

frappe.response['message'] = {
    'has_field': has_field,
    'docfield_rows': docfield_rows,
    'custom_field_rows': custom_field_rows,
    'has_column_in_pg': 'sales_invoice' in col_names
}
"""

script_payload = {
    'name': 'VM Check Sales Order Fields',
    'script_type': 'API',
    'api_method': 'vm_check_so_fields',
    'disabled': 0,
    'script': script_code
}

try:
    up_req = urllib.request.Request(f'{URL}/api/resource/Server%20Script/VM%20Check%20Sales%20Order%20Fields', data=json.dumps(script_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='PUT')
    op.open(up_req, timeout=15)
except Exception:
    create_req = urllib.request.Request(f'{URL}/api/resource/Server%20Script', data=json.dumps(script_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='POST')
    op.open(create_req, timeout=15)

req = urllib.request.Request(f'{URL}/api/method/vm_check_so_fields', headers=H)
res = op.open(req, timeout=15)
print('Result:', res.read().decode())
