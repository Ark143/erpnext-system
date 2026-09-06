import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'})

# Fetch all internal customers
int_custs = session.get(f'{BASE_URL}/api/resource/Customer?filters=[["is_internal_customer","=",1]]&fields=["name","customer_name","represents_company"]&limit_page_length=200').json().get('data', [])

print(f"=== CHECKING {len(int_custs)} INTERNAL CUSTOMERS ===")
for c in int_custs:
    doc = session.get(f"{BASE_URL}/api/resource/Customer/{requests.utils.quote(c['name'])}").json().get('data', {})
    allowed_cos = [x['company'] for x in doc.get('companies', [])]
    party_accs = [f"{x['company']}:{x.get('account')}" for x in doc.get('accounts', [])]
    print(f"Customer: {c['name']:<32} | Represents: {str(c.get('represents_company')):<30} | Allowed Companies: {len(allowed_cos)} | Accounts: {len(party_accs)}")

# Fetch all internal suppliers
int_supps = session.get(f'{BASE_URL}/api/resource/Supplier?filters=[["is_internal_supplier","=",1]]&fields=["name","supplier_name","represents_company"]&limit_page_length=200').json().get('data', [])

print(f"\n=== CHECKING {len(int_supps)} INTERNAL SUPPLIERS ===")
for s in int_supps:
    doc = session.get(f"{BASE_URL}/api/resource/Supplier/{requests.utils.quote(s['name'])}").json().get('data', {})
    allowed_cos = [x['company'] for x in doc.get('companies', [])]
    party_accs = [f"{x['company']}:{x.get('account')}" for x in doc.get('accounts', [])]
    print(f"Supplier: {s['name']:<32} | Represents: {str(s.get('represents_company')):<30} | Allowed Companies: {len(allowed_cos)} | Accounts: {len(party_accs)}")
