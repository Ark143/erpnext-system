import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Check if we can execute python on the server via Server Script or API
test_code = """
import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_mode_of_payments_info

try:
    res = get_mode_of_payments_info(('Cash',), 'Automan Car Care Center')
    frappe.response['message'] = {'status': 'success', 'data': res}
except Exception as e:
    import traceback
    frappe.response['message'] = {'status': 'error', 'error': str(e), 'traceback': traceback.format_exc()}
"""

script_payload = {
    "name": "Test POS Payment Info",
    "script_type": "API",
    "api_method": "test_pos_payment_info",
    "disabled": 0,
    "script": test_code
}

check_ss = s.get(f'{URL}/api/resource/Server%20Script/Test%20POS%20Payment%20Info')
if check_ss.status_code == 200:
    s.put(f'{URL}/api/resource/Server%20Script/Test%20POS%20Payment%20Info', json=script_payload)
else:
    s.post(f'{URL}/api/resource/Server%20Script', json=script_payload)

exec_res = s.get(f'{URL}/api/method/test_pos_payment_info')
print("Test result:", json.dumps(exec_res.json(), indent=2))
