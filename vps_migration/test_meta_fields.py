import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Let's test if we can fix the DocField link_filters in the database as well!
# In PostgreSQL, what happens if we alter column link_filters or set it to null or update it?
# Let's check what link_filters values exist:
script = """
# Let's see what happens if we test Exporter with a patched Exporter or if we test download_template
results = []
for dt in ['Item', 'Supplier', 'Batch', 'Customer Vehicle', 'Sales Invoice']:
    try:
        # Check meta fields
        meta = frappe.get_meta(dt)
        f_list = [f.fieldname for f in meta.fields if f.fieldtype not in ['Section Break', 'Column Break', 'Tab Break', 'HTML', 'Heading']]
        results.append({'doctype': dt, 'field_count': len(f_list)})
    except Exception as e:
        results.append({'doctype': dt, 'error': str(e)})

frappe.response['message'] = results
"""

s.put(f'{URL}/api/resource/Server Script/VM%20Test%20Debug', json={'script': script})
res = s.get(f'{URL}/api/method/vm_test_debug')
print(json.dumps(res.json(), indent=2))
