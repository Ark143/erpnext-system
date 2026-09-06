import requests, json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Fetch all User Permissions
res = s.get('http://38.247.138.224:10017/api/resource/User Permission?fields=["name","user","allow","for_value","is_default","apply_to_all_doctypes"]&limit_page_length=500').json()
print("=== USER PERMISSIONS ===")
for p in res.get('data', []):
    print(f"User: {p['user']} | Allow: {p['allow']} = {p['for_value']} | Apply All: {p.get('apply_to_all_doctypes')}")

# Fetch active users
users_res = s.get('http://38.247.138.224:10017/api/resource/User?filters=[["enabled","=",1],["user_type","=","System User"]]&fields=["name","email","full_name"]&limit_page_length=200').json()
print(f"\n=== ACTIVE SYSTEM USERS ({len(users_res.get('data', []))}) ===")
for u in users_res.get('data', []):
    print(f" - {u['name']} ({u['full_name']})")

# Check all POS Invoices by Company
inv_res = s.get('http://38.247.138.224:10017/api/resource/POS Invoice?fields=["name","company","customer","grand_total","owner","docstatus"]&limit_page_length=500').json()
invoices = inv_res.get('data', [])
print(f"\n=== TOTAL POS INVOICES: {len(invoices)} ===")
by_company = {}
for inv in invoices:
    co = inv['company']
    by_company.setdefault(co, []).append(inv['name'])
for co, inv_list in by_company.items():
    print(f"Company: {co} -> {len(inv_list)} invoices (e.g. {inv_list[:3]})")
