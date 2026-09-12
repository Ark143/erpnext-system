import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

script = """
ps = frappe.db.sql('''SELECT name, doc_type, field_name, property, value FROM "tabProperty Setter" WHERE property='link_filters' OR property LIKE '%filter%' ''', as_dict=True)

cfs = frappe.db.sql('''SELECT name, dt, fieldname, link_filters FROM "tabCustom Field" WHERE link_filters IS NOT NULL''', as_dict=True)

dfs = frappe.db.sql('''SELECT name, parent, fieldname, link_filters FROM "tabDocField" WHERE parent IN ('Item', 'Supplier', 'Batch')''', as_dict=True)

item_group_df = frappe.get_meta('Item').get_field('item_group')

frappe.response['message'] = {
    'property_setters': ps,
    'custom_fields': cfs,
    'item_docfields': dfs,
    'item_group_link_filters': item_group_df.get('link_filters') if item_group_df else None,
}
"""

s.put(f'{URL}/api/resource/Server Script/VM%20Test%20Debug', json={'script': script})
res = s.get(f'{URL}/api/method/vm_test_debug')
print(json.dumps(res.json(), indent=2))
