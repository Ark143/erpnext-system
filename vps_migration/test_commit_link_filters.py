import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

script = """
# In PostgreSQL, JSON columns accept valid JSON literals like 'null' or '{}'
docfields = frappe.db.sql('''SELECT name, parent, fieldname FROM "tabDocField" WHERE link_filters IS NOT NULL''', as_dict=True)
updated = []
for df in docfields:
    frappe.db.set_value('DocField', df['name'], 'link_filters', 'null', update_modified=False)
    updated.append(df['name'])

frappe.db.commit()
frappe.response['message'] = {'updated_count': len(updated), 'updated': updated}
"""

s.put(f'{URL}/api/resource/Server Script/VM%20Test%20Debug', json={'script': script})
res = s.post(f'{URL}/api/method/vm_test_debug')
print(json.dumps(res.json(), indent=2))
