import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

script = """
docfields = frappe.db.sql('''SELECT name, parent, fieldname FROM "tabDocField" WHERE link_filters IS NOT NULL''', as_dict=True)
updated = []
for df in docfields:
    frappe.db.set_value('DocField', df['name'], 'link_filters', None, update_modified=False)
    updated.append(df['name'])

frappe.response['message'] = {'updated_count': len(updated), 'updated': updated}
"""

s.put(f'{URL}/api/resource/Server Script/VM%20Test%20Debug', json={'script': script})
res = s.get(f'{URL}/api/method/vm_test_debug')
print(json.dumps(res.json(), indent=2))
