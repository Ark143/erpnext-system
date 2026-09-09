import requests
import json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# 1. Server Script for get_user_analytics_permissions
perm_script = """
user = frappe.session.user
all_comps = [c.name for c in frappe.get_all("Company", filters={"is_group": 0}, order_by="name asc") if c.name != "My Company"]

# Check executive roles
EXECUTIVE_ROLES = [
    "Administrator",
    "System Manager",
    "CEO",
    "Director",
    "Executive",
    "Operation",
    "Operations",
    "Operations Manager",
    "Finance",
    "Finance Manager",
    "Financial Officer",
    "Accounting",
    "Accounts Manager",
    "Accounts User",
    "Auditor"
]

if user == "Administrator":
    frappe.response['message'] = {
        'can_view_all': True,
        'allowed_companies': all_comps,
        'default_company': 'All Companies'
    }
else:
    # Query user roles from Has Role
    user_roles = frappe.get_all("Has Role", filters={"parent": user}, pluck="role")
    is_executive = False
    for r in user_roles:
        if r in EXECUTIVE_ROLES:
            is_executive = True
            break
            
    if is_executive:
        frappe.response['message'] = {
            'can_view_all': True,
            'allowed_companies': all_comps,
            'default_company': 'All Companies'
        }
    else:
        allowed = []
        # 1. From Employee
        emps = frappe.get_all("Employee", filters={"user_id": user}, fields=["company", "status"])
        for e in emps:
            c = e.get("company")
            if c and c not in allowed:
                allowed.append(c)
                
        # 2. From User Permission
        perms = frappe.get_all("User Permission", filters={"user": user, "allow": "Company"}, pluck="for_value")
        for c in perms:
            if c and c not in allowed:
                allowed.append(c)
                
        allowed.sort()
        def_comp = allowed[0] if allowed else (all_comps[0] if all_comps else "")
        frappe.response['message'] = {
            'can_view_all': False,
            'allowed_companies': allowed,
            'default_company': def_comp
        }
"""

res = s.put('http://38.247.138.224:10017/api/resource/Server Script/VM%20Get%20User%20Permissions', json={
    'doctype': 'Server Script',
    'name': 'VM Get User Permissions',
    'script': perm_script,
    'script_type': 'API',
    'api_method': 'vehicle_management.vehicle_management.analytics.get_user_analytics_permissions',
    'allow_guest': 0,
    'disabled': 0
})
if res.status_code not in [200, 201]:
    res = s.post('http://38.247.138.224:10017/api/resource/Server Script', json={
        'doctype': 'Server Script',
        'name': 'VM Get User Permissions',
        'script': perm_script,
        'script_type': 'API',
        'api_method': 'vehicle_management.vehicle_management.analytics.get_user_analytics_permissions',
        'allow_guest': 0,
        'disabled': 0
    })

print("Permission Server Script status:", res.status_code)

# Test calling the method as Administrator
r = s.get('http://38.247.138.224:10017/api/method/vehicle_management.vehicle_management.analytics.get_user_analytics_permissions')
print("Admin call status:", r.status_code)
print("Admin call result:", json.dumps(r.json(), indent=2))
