import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

# 1. Check roles in the system
roles_res = s.get(f"{VPS_BASE}/api/resource/Role?limit_page_length=300")
role_names = [r.get("name") for r in roles_res.json().get("data", [])]
print("All relevant Roles in system:")
for r in sorted(role_names):
    if any(k in r.lower() for k in ["admin", "ceo", "operat", "finan", "account", "manager", "director", "exec", "system"]):
        print(f" - {r}")

# 2. Check Employees in the system
emps_res = s.get(f"{VPS_BASE}/api/resource/Employee?limit_page_length=50&fields=[\"name\",\"employee_name\",\"user_id\",\"company\",\"status\"]")
emps = emps_res.json().get("data", [])
print(f"\nEmployees count on VPS: {len(emps)}")
for emp in emps[:15]:
    print(f" - {emp.get('name')} | User: {emp.get('user_id')} | Company: {emp.get('company')} | Name: {emp.get('employee_name')}")

# 3. Check Users on VPS
users_res = s.get(f"{VPS_BASE}/api/resource/User?limit_page_length=50&fields=[\"name\",\"full_name\",\"enabled\",\"user_type\"]")
users = users_res.json().get("data", [])
print(f"\nUsers count on VPS: {len(users)}")
for u in users[:15]:
    if u.get("name") not in ["Guest"]:
        print(f" - {u.get('name')} | Full Name: {u.get('full_name')} | Type: {u.get('user_type')}")
