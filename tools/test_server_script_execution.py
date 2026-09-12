import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Put a test script on Before Insert
s.put(f'{URL}/api/resource/Server%20Script/VM%20Validate%20Item%20Master', json={
    'doctype': 'Server Script',
    'script_type': 'DocType Event',
    'reference_doctype': 'Item',
    'doctype_event': 'Before Insert',
    'disabled': 0,
    'script': 'frappe.throw("TEST ITEM SERVER SCRIPT TRIGGERED!")'
})

res = s.post(f'{URL}/api/resource/Item', json={
    'doctype': 'Item',
    'item_code': 'TEST-FAIL-001',
    'item_name': 'Test Fail',
    'item_group': 'Products',
    'stock_uom': 'Unit'
})
print('Item Insert Response Status:', res.status_code)
print('Response body:', res.text[:300])
