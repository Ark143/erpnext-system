import requests
import json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# 1. Get all employees
emps = s.get('http://38.247.138.224:10017/api/resource/Employee?limit_page_length=100&fields=["name","employee_name","user_id","company","department","designation"]').json().get('data', [])
print('--- EMPLOYEES ---')
for e in emps:
    print(f"ID: {e.get('name')} | User: {e.get('user_id')} | Company: {e.get('company')} | Desig: {e.get('designation')}")

# 2. Get Users and Roles
users = s.get('http://38.247.138.224:10017/api/resource/User?limit_page_length=100&fields=["name","full_name","enabled"]').json().get('data', [])
print('\n--- USERS & ROLES ---')
for u in users:
    if u['name'] in ['Guest']:
        continue
    u_doc = s.get(f"http://38.247.138.224:10017/api/resource/User/{u['name']}").json().get('data', {})
    roles = [r.get('role') for r in u_doc.get('roles', [])]
    print(f"User: {u['name']} ({u['full_name']}) | Roles: {roles}")

# 3. Get User Permissions
perms = s.get('http://38.247.138.224:10017/api/resource/User Permission?limit_page_length=100').json().get('data', [])
print(f'\n--- USER PERMISSIONS ({len(perms)}) ---')
for p in perms:
    p_doc = s.get(f"http://38.247.138.224:10017/api/resource/User Permission/{p['name']}").json().get('data', {})
    print(f"User: {p_doc.get('user')} | Allow: {p_doc.get('allow')} | For: {p_doc.get('for_value')}")
