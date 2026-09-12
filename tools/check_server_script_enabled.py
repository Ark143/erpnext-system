import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Let's inspect Server Script settings via API
api_script = """
import frappe
frappe.response['message'] = {
    'server_script_enabled': frappe.conf.get('server_script_enabled'),
    'developer_mode': frappe.conf.get('developer_mode')
}
"""

res_post = s.put(f'{URL}/api/resource/Server%20Script/vm_check_conf', json={
    'doctype': 'Server Script',
    'name': 'vm_check_conf',
    'script_type': 'API',
    'api_method': 'vm_check_conf',
    'allow_guest': 0,
    'disabled': 0,
    'script': api_script
})
if res_post.status_code not in [200, 201]:
    s.post(f'{URL}/api/resource/Server%20Script', json={
        'doctype': 'Server Script',
        'name': 'vm_check_conf',
        'script_type': 'API',
        'api_method': 'vm_check_conf',
        'allow_guest': 0,
        'disabled': 0,
        'script': api_script
    })

res = s.get(f'{URL}/api/method/vm_check_conf')
print('Frappe Conf Check:', res.json())
