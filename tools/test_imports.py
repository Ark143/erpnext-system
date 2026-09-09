import requests
s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

test_script = """
import frappe
from frappe.utils import flt, nowdate, add_months, getdate
frappe.response['message'] = 'Imports successful!'
"""

res = s.put('http://38.247.138.224:10017/api/resource/Server Script/VM%20Test%20Module', json={
    'doctype': 'Server Script',
    'name': 'VM Test Module',
    'script': test_script,
    'script_type': 'API',
    'api_method': 'vm_test_module',
    'allow_guest': 0,
    'disabled': 0
})
r = s.get('http://38.247.138.224:10017/api/method/vm_test_module')
print(r.status_code, r.text)
