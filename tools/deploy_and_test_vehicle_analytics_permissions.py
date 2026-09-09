import requests
import json
import urllib.parse

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
login_res = s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})
print("Administrator Login Status:", login_res.status_code)

# Read the local files
with open("frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/analytics.py", "r", encoding="utf-8") as f:
    analytics_py_content = f.read()

with open("frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/page/vehicle_analytics/vehicle_analytics.js", "r", encoding="utf-8") as f:
    analytics_js_content = f.read()

# Server script to deploy both files onto VPS disk
deploy_script = f"""
def deploy_files():
    import os
    import importlib
    
    analytics_path = frappe.get_app_path("vehicle_management", "vehicle_management", "analytics.py")
    page_js_path = frappe.get_app_path("vehicle_management", "vehicle_management", "page", "vehicle_analytics", "vehicle_analytics.js")
    public_js_path = frappe.get_app_path("vehicle_management", "public", "js", "vehicle_analytics.js")

    os.makedirs(os.path.dirname(analytics_path), exist_ok=True)
    with open(analytics_path, "w", encoding="utf-8") as f:
        f.write({repr(analytics_py_content)})

    os.makedirs(os.path.dirname(page_js_path), exist_ok=True)
    with open(page_js_path, "w", encoding="utf-8") as f:
        f.write({repr(analytics_js_content)})

    os.makedirs(os.path.dirname(public_js_path), exist_ok=True)
    with open(public_js_path, "w", encoding="utf-8") as f:
        f.write({repr(analytics_js_content)})

    # Reload module in memory
    vm_mod = frappe.get_module("vehicle_management.vehicle_management.analytics")
    importlib.reload(vm_mod)
    frappe.clear_cache()

    frappe.response["message"] = {{
        "status": "success",
        "analytics_path": analytics_path,
        "page_js_path": page_js_path,
        "public_js_path": public_js_path
    }}

deploy_files()
"""

# Push Server Script to VPS
res = s.put(f"{VPS_BASE}/api/resource/Server Script/VM%20Deploy%20Analytics%20Patch", json={
    "doctype": "Server Script",
    "name": "VM Deploy Analytics Patch",
    "script": deploy_script,
    "script_type": "API",
    "api_method": "vm_deploy_analytics_patch",
    "allow_guest": 1,
    "disabled": 0
})
if res.status_code not in [200, 201]:
    res = s.post(f"{VPS_BASE}/api/resource/Server Script", json={
        "doctype": "Server Script",
        "name": "VM Deploy Analytics Patch",
        "script": deploy_script,
        "script_type": "API",
        "api_method": "vm_deploy_analytics_patch",
        "allow_guest": 1,
        "disabled": 0
    })
print("Server Script Update Status:", res.status_code)

# Trigger Deployment
deploy_call = s.get(f"{VPS_BASE}/api/method/vm_deploy_analytics_patch")
print("Deployment Response:", deploy_call.status_code, deploy_call.text)

# Test Permissions and Scoping for Administrator
print("\n=== TESTING ADMINISTRATOR (EXECUTIVE / ALL COMPANIES ACCESS) ===")
perm_admin = s.get(f"{VPS_BASE}/api/method/vehicle_management.vehicle_management.analytics.get_user_analytics_permissions").json()
print("Admin Permissions:", json.dumps(perm_admin.get("message", {}), indent=2))

admin_analytics = s.get(f"{VPS_BASE}/api/method/vehicle_management.vehicle_management.analytics.get_vehicle_management_analytics", params={
    "company": "All Companies",
    "timespan": "Last 30 Days"
}).json()
print("Admin Total Revenue:", admin_analytics.get("message", {}).get("summary", {}).get("total_revenue"))
print("Admin Companies Count in Performance:", len(admin_analytics.get("message", {}).get("company_performance", [])))

# Test User Scoping via Server Script
test_user_script = """
def test_scoping():
    target_user = frappe.form_dict.get('user', 'jayson.espiritu@ultramrf.ph')
    vm_mod = frappe.get_module("vehicle_management.vehicle_management.analytics")
    
    # 1. Get permissions for target user
    perm = vm_mod.get_user_analytics_permissions(user=target_user)
    
    # 2. Simulate execution as target_user
    orig_user = frappe.session.user
    try:
        frappe.session.user = target_user
        res_data = vm_mod.get_vehicle_management_analytics(company="All Companies", timespan="Last 30 Days")
    finally:
        frappe.session.user = orig_user

    frappe.response['message'] = {
        'user': target_user,
        'permissions': perm,
        'summary': res_data.get('summary'),
        'companies': [c.get('company') for c in res_data.get('company_performance', [])],
        'top_services_count': len(res_data.get('top_services', [])),
        'top_parts_count': len(res_data.get('top_parts', []))
    }

test_scoping()
"""

res_test = s.put(f"{VPS_BASE}/api/resource/Server Script/VM%20Test%20User%20Scoping", json={
    "doctype": "Server Script",
    "name": "VM Test User Scoping",
    "script": test_user_script,
    "script_type": "API",
    "api_method": "vm_test_user_scoping",
    "allow_guest": 1,
    "disabled": 0
})
if res_test.status_code not in [200, 201]:
    res_test = s.post(f"{VPS_BASE}/api/resource/Server Script", json={
        "doctype": "Server Script",
        "name": "VM Test User Scoping",
        "script": test_user_script,
        "script_type": "API",
        "api_method": "vm_test_user_scoping",
        "allow_guest": 1,
        "disabled": 0
    })

test_users = [
    "jayson.espiritu@ultramrf.ph",
    "jasper.david@ultramrf.ph",
    "salvador.torrecampo@ultramrf.ph",
    "testdau@gmail.com",
    "test@gmail.com",
    "test12@gmail.com",
    "whsdau@gmail.com"
]

print("\n=== TESTING BRANCH USERS SCOPING ===")
for u in test_users:
    call_test = s.get(f"{VPS_BASE}/api/method/vm_test_user_scoping", params={"user": u}).json()
    msg = call_test.get("message", {})
    perm = msg.get("permissions", {})
    print(f"\nUser: {u}")
    print(f"  - can_view_all: {perm.get('can_view_all')}")
    print(f"  - allowed_companies: {perm.get('allowed_companies')}")
    print(f"  - default_company: {perm.get('default_company')}")
    print(f"  - Scoped Branches in Dashboard: {msg.get('companies')}")
    print(f"  - Scoped Total Revenue: {msg.get('summary', {}).get('total_revenue')}")
    print(f"  - Scoped Total JOs: {msg.get('summary', {}).get('total_jos')}")
