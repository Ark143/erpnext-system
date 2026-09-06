import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
login_res = session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)
login_res.raise_for_status()

# 1. Fetch all companies
comp_res = session.get(f"{BASE_URL}/api/resource/Company?fields=[\"name\",\"abbr\"]&limit_page_length=100").json()
companies = [c['name'] for c in comp_res.get('data', [])]

# 2. Fetch all internal customers
int_custs = session.get(f'{BASE_URL}/api/resource/Customer?filters=[["is_internal_customer","=",1]]&fields=["name","customer_name","represents_company","is_internal_customer"]&limit_page_length=200').json().get('data', [])

# 3. Fetch all internal suppliers
int_supps = session.get(f'{BASE_URL}/api/resource/Supplier?filters=[["is_internal_supplier","=",1]]&fields=["name","supplier_name","represents_company","is_internal_supplier"]&limit_page_length=200').json().get('data', [])

cust_map = {c['represents_company']: c for c in int_custs if c.get('represents_company')}
supp_map = {s['represents_company']: s for s in int_supps if s.get('represents_company')}

print("="*105)
print(f"{'COMPANY':<35} | {'INTERNAL CUSTOMER':<32} | {'INTERNAL SUPPLIER':<32}")
print("="*105)

missing_count = 0
for co in companies:
    cust = cust_map.get(co)
    supp = supp_map.get(co)
    
    cust_name = cust['name'] if cust else "❌ MISSING"
    supp_name = supp['name'] if supp else "❌ MISSING"
    
    if not cust or not supp:
        missing_count += 1
        
    print(f"{co:<35} | {cust_name:<32} | {supp_name:<32}")

print("="*105)
print(f"Total Companies: {len(companies)} | Successfully Configured: {len(companies) - missing_count}/{len(companies)}")

# Check child tables (Allowed to Transact With) on a sample
sample_cust = session.get(f"{BASE_URL}/api/resource/Customer/{requests.utils.quote(companies[0])}").json().get('data', {})
sample_supp = session.get(f"{BASE_URL}/api/resource/Supplier/{requests.utils.quote(companies[0])}").json().get('data', {})

print(f"\nVerification of Transact Companies Child Table for '{companies[0]}':")
print(f" - Customer allowed companies count: {len(sample_cust.get('companies', []))}")
print(f" - Supplier allowed companies count: {len(sample_supp.get('companies', []))}")
