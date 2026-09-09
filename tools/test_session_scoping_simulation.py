import requests
import json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

test_script = """
users = [
    "Administrator",
    "jayson.espiritu@ultramrf.ph",
    "jasper.david@ultramrf.ph",
    "salvador.torrecampo@ultramrf.ph",
    "testdau@gmail.com",
    "test@gmail.com",
    "test12@gmail.com",
    "whsdau@gmail.com"
]

analytics_doc = frappe.get_doc("Server Script", "VM Get Vehicle Analytics")
perm_doc = frappe.get_doc("Server Script", "VM Get User Permissions")

output_results = []
for u in users:
    orig_user = frappe.session.user
    try:
        frappe.session.user = u
        frappe.form_dict = {'company': 'All Companies', 'timespan': 'Last 30 Days'}
        
        # Execute analytics server script
        analytics_doc.execute_method()
        res_data = frappe.response.get('message', {})
        
        # Execute perm server script
        perm_doc.execute_method()
        perm_data = frappe.response.get('message', {})
        
        output_results.append({
            'user': u,
            'can_view_all': perm_data.get('can_view_all'),
            'allowed_companies': perm_data.get('allowed_companies'),
            'default_company': perm_data.get('default_company'),
            'total_revenue': res_data.get('summary', {}).get('total_revenue'),
            'total_jos': res_data.get('summary', {}).get('total_jos'),
            'branches_displayed': [b.get('company') for b in res_data.get('company_performance', [])]
        })
    finally:
        frappe.session.user = orig_user

frappe.response['message'] = output_results
"""

res = s.put('http://38.247.138.224:10017/api/resource/Server Script/VM%20Test%20Full%20Session%20Scoping', json={
    'doctype': 'Server Script',
    'name': 'VM Test Full Session Scoping',
    'script': test_script,
    'script_type': 'API',
    'api_method': 'vm_test_full_session_scoping',
    'allow_guest': 0,
    'disabled': 0
})
if res.status_code not in [200, 201]:
    res = s.post('http://38.247.138.224:10017/api/resource/Server Script', json={
        'doctype': 'Server Script',
        'name': 'VM Test Full Session Scoping',
        'script': test_script,
        'script_type': 'API',
        'api_method': 'vm_test_full_session_scoping',
        'allow_guest': 0,
        'disabled': 0
    })

r = s.get('http://38.247.138.224:10017/api/method/vm_test_full_session_scoping')
print("Session Scoping Simulation Results:")
for row in r.json().get('message', []):
    print(f"\nUser: {row['user']}")
    print(f"  - Full Access (can_view_all): {row['can_view_all']}")
    print(f"  - Allowed Companies: {row['allowed_companies']}")
    print(f"  - Default Company: {row['default_company']}")
    print(f"  - Scoped Revenue: PHP {row['total_revenue']:,.2f}")
    print(f"  - Scoped JO Count: {row['total_jos']}")
    print(f"  - Branches Displayed: {row['branches_displayed']}")
