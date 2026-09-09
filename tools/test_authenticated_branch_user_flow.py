import requests
import json
import urllib.parse

VPS_BASE = "http://38.247.138.224:10017"

# 1. Login as Administrator
admin_s = requests.Session()
admin_s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

test_users_info = [
    ("jayson.espiritu@ultramrf.ph", "Automan Car Care Center", "Automan@2026#SecureBranch!"),
    ("jasper.david@ultramrf.ph", "Wheel Core", "WheelCore@2026#SecureBranch!"),
    ("salvador.torrecampo@ultramrf.ph", "The Wheelhub", "WheelHub@2026#SecureBranch!")
]

for user_email, expected_branch, strong_pwd in test_users_info:
    # Set password via Administrator
    admin_s.put(f"{VPS_BASE}/api/resource/User/{urllib.parse.quote(user_email)}", json={
        "new_password": strong_pwd
    })
    
    # Fresh session as branch user
    user_s = requests.Session()
    lr = user_s.post(f"{VPS_BASE}/api/method/login", data={"usr": user_email, "pwd": strong_pwd})
    print(f"\n=================================================================")
    print(f"AUTHENTICATED USER TEST: {user_email}")
    print(f"Login Response: {lr.status_code} | Name: {lr.json().get('full_name')}")
    print(f"=================================================================")
    
    # 1. Test get_user_analytics_permissions
    perm_res = user_s.get(f"{VPS_BASE}/api/method/vehicle_management.vehicle_management.analytics.get_user_analytics_permissions")
    perm_data = perm_res.json().get("message", {})
    print(f"Permissions for {user_email}:")
    print(f" - can_view_all: {perm_data.get('can_view_all')}")
    print(f" - allowed_companies: {perm_data.get('allowed_companies')}")
    print(f" - default_company: {perm_data.get('default_company')}")
    
    # 2. Test get_vehicle_management_analytics (Passing All Companies to test security restriction)
    analytics_res = user_s.get(f"{VPS_BASE}/api/method/vehicle_management.vehicle_management.analytics.get_vehicle_management_analytics", params={
        "company": "All Companies",
        "timespan": "Last 30 Days"
    })
    analytics_data = analytics_res.json().get("message", {})
    summary = analytics_data.get("summary", {})
    company_perf = analytics_data.get("company_performance", [])
    
    print(f"\nScoped Analytics Data:")
    print(f" - Total Revenue: PHP {summary.get('total_revenue', 0):,.2f}")
    print(f" - Total Labor: PHP {summary.get('total_labor', 0):,.2f}")
    print(f" - Total Parts: PHP {summary.get('total_parts', 0):,.2f}")
    print(f" - Total Job Orders: {summary.get('total_jos', 0)}")
    print(f" - Unique Vehicles: {summary.get('unique_vehicles', 0)}")
    print(f" - Branches in Performance breakdown: {[b.get('company') for b in company_perf]}")
    
    assert perm_data.get("can_view_all") == False, f"Expected can_view_all=False for {user_email}"
    assert perm_data.get("allowed_companies") == [expected_branch], f"Expected only {[expected_branch]}, got {perm_data.get('allowed_companies')}"
    assert len(company_perf) == 1 and company_perf[0].get("company") == expected_branch, f"Branch performance table breached! Got {[b.get('company') for b in company_perf]}"
    print(f"SUCCESS: Access control verified strictly for {expected_branch}!")

print("\nALL AUTHENTICATED BRANCH TESTS PASSED PERFECTLY!")
