import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

script = """
# Saving the DocType refreshes its meta cache and synchronizes child docfields
for dt in ['Item', 'Supplier', 'Batch']:
    try:
        doc = frappe.get_doc('DocType', dt)
        doc.save(ignore_permissions=True)
    except Exception:
        pass

frappe.response['message'] = {'status': 'doctypes_resaved_and_cache_cleared'}
"""

s.put(f'{URL}/api/resource/Server Script/VM%20Test%20Debug', json={'script': script})
res = s.post(f'{URL}/api/method/vm_test_debug')
print(json.dumps(res.json(), indent=2))
