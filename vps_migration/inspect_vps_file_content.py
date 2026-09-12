import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Let's inspect base_document.py on the VPS using VM Test Debug
patch_script = """
import frappe.model.base_document as bd
import frappe.core.doctype.data_import.exporter as exp

bd_path = bd.__file__
exp_path = exp.__file__

with open(bd_path, 'r', encoding='utf-8') as f:
    bd_content = f.read()
    
with open(exp_path, 'r', encoding='utf-8') as f:
    exp_content = f.read()
    
idx = bd_content.find('cannot be a list')
snippet = bd_content[max(0, idx-200):min(len(bd_content), idx+200)] if idx != -1 else 'Not found'

frappe.response['message'] = {
    'bd_path': bd_path,
    'exp_path': exp_path,
    'bd_snippet': snippet
}
"""

server_script_payload = {
    'doctype': 'Server Script',
    'name': 'VM Test Debug',
    'script_type': 'API',
    'api_method': 'vm_test_debug',
    'allow_guest': 1,
    'disabled': 0,
    'script': patch_script
}

s.put(f'{URL}/api/resource/Server Script/VM%20Test%20Debug', json=server_script_payload)
r = s.get(f'{URL}/api/method/vm_test_debug')
print(json.dumps(r.json(), indent=2))
