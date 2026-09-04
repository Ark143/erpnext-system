import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

# Build a robust, bulletproof get_open_count API for Vehicle Management doctypes
script_code = """
doctype = frappe.form_dict.get('doctype')
name = frappe.form_dict.get('name')
items_raw = frappe.form_dict.get('items')

if isinstance(items_raw, str):
    try:
        import json
        items = json.loads(items_raw)
    except Exception:
        items = []
elif isinstance(items_raw, list):
    items = items_raw
else:
    items = []

internal_links_found = []
external_links_found = []

if doctype and name and frappe.db.exists(doctype, name):
    doc = frappe.get_doc(doctype, name)
    
    if doctype == 'Vehicle Job Order':
        # Internal links (on doc itself)
        if doc.get('customer'):
            internal_links_found.append({
                'doctype': 'Customer',
                'count': 1,
                'open_count': 0,
                'names': [doc.get('customer')]
            })
        if doc.get('vehicle'):
            internal_links_found.append({
                'doctype': 'Customer Vehicle',
                'count': 1,
                'open_count': 0,
                'names': [doc.get('vehicle')]
            })
        if doc.get('estimate'):
            internal_links_found.append({
                'doctype': 'Vehicle Estimate',
                'count': 1,
                'open_count': 0,
                'names': [doc.get('estimate')]
            })
            
        # External linked transactions (referencing this JO)
        for dt, fld in [
            ('Sales Invoice', 'custom_vehicle_job_order'),
            ('Sales Order', 'custom_vehicle_job_order'),
            ('Quotation', 'custom_vehicle_job_order'),
            ('Vehicle Inspection', 'job_order')
        ]:
            if 'items' not in frappe.form_dict or not items or dt in items:
                cnt = 0
                try:
                    meta = frappe.get_meta(dt)
                    if meta.has_field(fld):
                        cnt = len(frappe.get_all(dt, filters={fld: name}, limit=100))
                except Exception:
                    cnt = 0
                external_links_found.append({
                    'doctype': dt,
                    'count': cnt,
                    'open_count': 0
                })

    elif doctype == 'Vehicle Estimate':
        if doc.get('customer'):
            internal_links_found.append({
                'doctype': 'Customer',
                'count': 1,
                'open_count': 0,
                'names': [doc.get('customer')]
            })
        if doc.get('vehicle'):
            internal_links_found.append({
                'doctype': 'Customer Vehicle',
                'count': 1,
                'open_count': 0,
                'names': [doc.get('vehicle')]
            })
        if doc.get('job_order'):
            internal_links_found.append({
                'doctype': 'Vehicle Job Order',
                'count': 1,
                'open_count': 0,
                'names': [doc.get('job_order')]
            })

    elif doctype == 'Customer Vehicle':
        if doc.get('customer'):
            internal_links_found.append({
                'doctype': 'Customer',
                'count': 1,
                'open_count': 0,
                'names': [doc.get('customer')]
            })
        for dt, fld in [
            ('Vehicle Job Order', 'vehicle'),
            ('Vehicle Estimate', 'vehicle'),
            ('Vehicle Inspection', 'vehicle'),
            ('Sales Invoice', 'custom_vehicle_plate')
        ]:
            if 'items' not in frappe.form_dict or not items or dt in items:
                cnt = 0
                try:
                    meta = frappe.get_meta(dt)
                    if meta.has_field(fld):
                        cnt = len(frappe.get_all(dt, filters={fld: name}, limit=100))
                except Exception:
                    cnt = 0
                external_links_found.append({
                    'doctype': dt,
                    'count': cnt,
                    'open_count': 0
                })

frappe.response['message'] = {
    'count': {
        'internal_links_found': internal_links_found,
        'external_links_found': external_links_found
    }
}
"""

name = "VM Safe Open Count API"
payload = {
    'name': name,
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_get_open_count',
    'allow_guest': 0,
    'disabled': 0,
    'script': script_code
}

req = urllib.request.Request(f"{URL}/api/resource/Server%20Script/{urllib.parse.quote(name)}", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
try:
    req.get_method = lambda: 'PUT'
    op.open(req)
    print("Updated Server Script 'VM Safe Open Count API'")
except Exception:
    req = urllib.request.Request(f"{URL}/api/resource/Server%20Script", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
    op.open(req)
    print("Created Server Script 'VM Safe Open Count API'")

# Test calling the new API with the exact payload that failed
body = urllib.parse.urlencode({
    'doctype': 'Vehicle Job Order',
    'name': 'JO-2026-00204',
    'items': json.dumps(['Vehicle Estimate', 'Sales Invoice', 'Sales Order', 'Quotation', 'Customer Vehicle', 'Customer'])
}).encode()

res = op.open(urllib.request.Request(f'{URL}/api/method/vm_get_open_count', data=body, headers=H))
print("Safe Open Count Response:")
print(json.dumps(json.loads(res.read().decode()), indent=2))
