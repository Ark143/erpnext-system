import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

script = """
# Test calling frappe.cache() method
cache_client = frappe.cache()
keys = cache_client.get_keys('meta:')
deleted = 0
for k in keys:
    cache_client.delete_value(k)
    deleted += 1

# Also clear doctype schema cache
cache_client.delete_keys('meta:*')
cache_client.delete_keys('doctype:*')
cache_client.delete_keys('table_columns:*')

frappe.response['message'] = {'deleted_keys_count': deleted}
"""

s.put(f'{URL}/api/resource/Server Script/VM%20Test%20Debug', json={'script': script})
res = s.post(f'{URL}/api/method/vm_test_debug')
print(json.dumps(res.json(), indent=2))
