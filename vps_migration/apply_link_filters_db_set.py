import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

script = """
# Clear link_filters on all DocFields using db_set and save
docfield_names = [r['name'] for r in frappe.db.sql('''SELECT name FROM "tabDocField" WHERE link_filters IS NOT NULL''', as_dict=True)]
fixed = []
for name in docfield_names:
    d = frappe.get_doc('DocField', name)
    d.link_filters = None
    d.db_set('link_filters', None, update_modified=False)
    fixed.append(name)

frappe.response['message'] = {'fixed_count': len(fixed), 'fixed': fixed}
"""

s.put(f'{URL}/api/resource/Server Script/VM%20Test%20Debug', json={'script': script})
res = s.get(f'{URL}/api/method/vm_test_debug')
print(json.dumps(res.json(), indent=2))
