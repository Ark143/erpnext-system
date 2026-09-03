import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

script_code = """
frappe.db.set_value('Dashboard Chart', 'Vehicle POS Sales by Company', {
    'document_type': 'POS Invoice',
    'aggregate_function_based_on': 'grand_total',
    'group_by_based_on': 'company'
}, update_modified=False)
frappe.db.commit()
frappe.response['message'] = 'Updated Dashboard Chart via DB'
"""

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote('Probe API'),
    data=json.dumps({'script': script_code}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)
opener.open(req)

res = opener.open('http://38.247.138.224:10017/api/method/vm_probe_api')
print(res.read().decode())
