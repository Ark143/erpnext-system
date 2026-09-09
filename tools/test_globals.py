import requests
s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

test_script = """
flt = frappe.utils.flt
nowdate = frappe.utils.nowdate
roles = frappe.get_roles(frappe.session.user)
comps = frappe.get_all("Company", pluck="name")
frappe.response['message'] = {
    'user': frappe.session.user,
    'roles': roles,
    'companies': comps
}
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
