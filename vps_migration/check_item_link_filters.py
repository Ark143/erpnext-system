import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

script = """
# Test what happens when Item DocFields link_filters are checked
dfs = frappe.db.sql('''SELECT name, parent, fieldname, link_filters FROM "tabDocField" WHERE parent='Item' AND link_filters IS NOT NULL''', as_dict=True)
frappe.response['message'] = dfs
"""

s.put(f'{URL}/api/resource/Server Script/VM%20Test%20Debug', json={'script': script})
res = s.get(f'{URL}/api/method/vm_test_debug')
print(json.dumps(res.json(), indent=2))
