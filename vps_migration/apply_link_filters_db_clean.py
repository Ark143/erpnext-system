import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

script = """
# Let's see what happens if we set link_filters = NULL on tabDocField and tabCustom Field
frappe.db.sql('''UPDATE "tabDocField" SET link_filters = NULL WHERE link_filters IS NOT NULL''')
frappe.db.sql('''UPDATE "tabCustom Field" SET link_filters = NULL WHERE link_filters IS NOT NULL''')
frappe.db.commit()
frappe.clear_cache()

frappe.response['message'] = {'status': 'updated_and_cache_cleared'}
"""

s.put(f'{URL}/api/resource/Server Script/VM%20Test%20Debug', json={'script': script})
res = s.get(f'{URL}/api/method/vm_test_debug')
print(json.dumps(res.json(), indent=2))
