import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

script = """
dfs = frappe.db.sql('''SELECT name, parent, fieldname, link_filters FROM "tabDocField" WHERE link_filters IS NOT NULL''', as_dict=True)
cfs = frappe.db.sql('''SELECT name, dt, fieldname, link_filters FROM "tabCustom Field" WHERE link_filters IS NOT NULL''', as_dict=True)

frappe.response['message'] = {
    'docfields_count': len(dfs),
    'docfields_sample': dfs[:5],
    'customfields_count': len(cfs),
    'customfields_sample': cfs[:5]
}
"""

s.put(f'{URL}/api/resource/Server Script/VM%20Test%20Debug', json={'script': script})
res = s.get(f'{URL}/api/method/vm_test_debug')
print(json.dumps(res.json(), indent=2))
