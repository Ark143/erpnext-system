import requests
s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

test_script = """
vm_analytics = frappe.get_module("vehicle_management.vehicle_management.analytics")
# Let's inspect what is available
frappe.response["message"] = {
    "vm_analytics": str(vm_analytics),
    "get_app_path": frappe.get_app_path("vehicle_management")
}
"""

res = s.put('http://38.247.138.224:10017/api/resource/Server Script/VM%20Test%20Module', json={
    'doctype': 'Server Script',
    'name': 'VM Test Module',
    'script': test_script,
    'script_type': 'API',
    'api_method': 'vm_test_module',
    'allow_guest': 1,
    'disabled': 0
})
if res.status_code not in [200, 201]:
    res = s.post('http://38.247.138.224:10017/api/resource/Server Script', json={
        'doctype': 'Server Script',
        'name': 'VM Test Module',
        'script': test_script,
        'script_type': 'API',
        'api_method': 'vm_test_module',
        'allow_guest': 1,
        'disabled': 0
    })

r = s.get('http://38.247.138.224:10017/api/method/vm_test_module')
print(r.status_code, r.text)
