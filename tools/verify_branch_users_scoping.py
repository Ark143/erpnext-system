import requests
import json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

eval_users_script = """
users_to_test = [
    "jayson.espiritu@ultramrf.ph",
    "jasper.david@ultramrf.ph",
    "salvador.torrecampo@ultramrf.ph",
    "testdau@gmail.com",
    "test@gmail.com",
    "test12@gmail.com",
    "whsdau@gmail.com"
]

all_comps = [c.name for c in frappe.get_all("Company", filters={"is_group": 0}, order_by="name asc") if c.name != "My Company"]

results = []
for u in users_to_test:
    allowed = []
    emps = frappe.get_all("Employee", filters={"user_id": u}, fields=["company", "status"])
    for e in emps:
        c = e.get("company")
        if c and c not in allowed and c != "My Company":
            allowed.append(c)
            
    perms = frappe.get_all("User Permission", filters={"user": u, "allow": "Company"}, pluck="for_value")
    for c in perms:
        if c and c not in allowed and c != "My Company":
            allowed.append(c)
            
    allowed.sort()
    
    jos = frappe.get_all("Vehicle Job Order", filters={"docstatus": ["!=", 2], "company": ["in", allowed]}, fields=["name", "company", "grand_total"])
    tot_rev = sum(frappe.utils.flt(j.grand_total) for j in jos)
    
    results.append({
        "user": u,
        "employee_company": emps[0].get("company") if emps else "None",
        "allowed_companies": allowed,
        "can_view_all": False,
        "scoped_jos_count": len(jos),
        "scoped_revenue": tot_rev
    })

frappe.response['message'] = results
"""

res = s.put('http://38.247.138.224:10017/api/resource/Server Script/VM%20Verify%20All%20Branch%20Users', json={
    'doctype': 'Server Script',
    'name': 'VM Verify All Branch Users',
    'script': eval_users_script,
    'script_type': 'API',
    'api_method': 'vm_verify_all_branch_users',
    'allow_guest': 0,
    'disabled': 0
})
if res.status_code not in [200, 201]:
    res = s.post('http://38.247.138.224:10017/api/resource/Server Script', json={
        'doctype': 'Server Script',
        'name': 'VM Verify All Branch Users',
        'script': eval_users_script,
        'script_type': 'API',
        'api_method': 'vm_verify_all_branch_users',
        'allow_guest': 0,
        'disabled': 0
    })

r = s.get('http://38.247.138.224:10017/api/method/vm_verify_all_branch_users')
print('Status:', r.status_code)
for item in r.json().get('message', []):
    print(f"User: {item['user']:<32} | Company: {item['employee_company']:<25} | Allowed: {str(item['allowed_companies']):<30} | JOs: {item['scoped_jos_count']:<3} | Revenue: PHP {item['scoped_revenue']:,.2f}")
