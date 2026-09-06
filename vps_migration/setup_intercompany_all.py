import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
login_res = session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)
login_res.raise_for_status()
print("[OK] Logged in to ERPNext as Administrator")

# 1. Fetch all companies
comp_res = session.get(f"{BASE_URL}/api/resource/Company?fields=[\"name\",\"abbr\"]&limit_page_length=100").json()
companies = [c['name'] for c in comp_res.get('data', [])]
print(f"\nFound {len(companies)} companies:")
for co in companies:
    print(f" - {co}")

# Helper to fetch all records
def get_all(doctype, fields):
    res = session.get(f"{BASE_URL}/api/resource/{requests.utils.quote(doctype)}?fields={json.dumps(fields)}&limit_page_length=1000").json()
    return res.get('data', [])

existing_customers = get_all('Customer', ['name', 'customer_name', 'is_internal_customer', 'represents_company'])
existing_suppliers = get_all('Supplier', ['name', 'supplier_name', 'is_internal_supplier', 'represents_company'])

# Build allowed companies list for child tables
allowed_companies_list = [{'company': c} for c in companies]

print("\n" + "="*60)
print("SETTING UP INTERCOMPANY CUSTOMERS FOR ALL COMPANIES")
print("="*60)

for co in companies:
    # Check if a customer matches this company
    match = None
    for cust in existing_customers:
        if cust.get('represents_company') == co:
            match = cust
            break
        if cust.get('customer_name', '').strip().lower() == co.strip().lower():
            match = cust
            break
        if cust.get('name', '').strip().lower() == co.strip().lower():
            match = cust
            break

    cust_payload = {
        'customer_name': co,
        'customer_type': 'Company',
        'customer_group': 'Commercial',
        'territory': 'All Territories',
        'is_internal_customer': 1,
        'represents_company': co,
        'companies': allowed_companies_list
    }

    if match:
        doc_name = match['name']
        print(f"Updating existing Customer: '{doc_name}' for company '{co}'...", flush=True)
        r = session.put(f"{BASE_URL}/api/resource/Customer/{requests.utils.quote(doc_name)}", json=cust_payload, timeout=30)
        if r.status_code == 200:
            print(f"  [OK] Updated Customer: {doc_name}")
        else:
            print(f"  [ERROR] Updating {doc_name}: {r.status_code} - {r.text}")
    else:
        print(f"Creating new Customer for company '{co}'...", flush=True)
        r = session.post(f"{BASE_URL}/api/resource/Customer", json=cust_payload, timeout=30)
        if r.status_code == 200:
            created = r.json().get('data', {})
            print(f"  [OK] Created Customer: {created.get('name')}")
        else:
            print(f"  [ERROR] Creating Customer for {co}: {r.status_code} - {r.text}")

print("\n" + "="*60)
print("SETTING UP INTERCOMPANY SUPPLIERS FOR ALL COMPANIES")
print("="*60)

for co in companies:
    # Check if a supplier matches this company
    match = None
    for sup in existing_suppliers:
        if sup.get('represents_company') == co:
            match = sup
            break
        if sup.get('supplier_name', '').strip().lower() == co.strip().lower():
            match = sup
            break
        if sup.get('name', '').strip().lower() == co.strip().lower():
            match = sup
            break

    supp_payload = {
        'supplier_name': co,
        'supplier_type': 'Company',
        'supplier_group': 'All Supplier Groups',
        'is_internal_supplier': 1,
        'represents_company': co,
        'companies': allowed_companies_list
    }

    if match:
        doc_name = match['name']
        print(f"Updating existing Supplier: '{doc_name}' for company '{co}'...", flush=True)
        r = session.put(f"{BASE_URL}/api/resource/Supplier/{requests.utils.quote(doc_name)}", json=supp_payload, timeout=30)
        if r.status_code == 200:
            print(f"  [OK] Updated Supplier: {doc_name}")
        else:
            print(f"  [ERROR] Updating {doc_name}: {r.status_code} - {r.text}")
    else:
        print(f"Creating new Supplier for company '{co}'...", flush=True)
        r = session.post(f"{BASE_URL}/api/resource/Supplier", json=supp_payload, timeout=30)
        if r.status_code == 200:
            created = r.json().get('data', {})
            print(f"  [OK] Created Supplier: {created.get('name')}")
        else:
            print(f"  [ERROR] Creating Supplier for {co}: {r.status_code} - {r.text}")

print("\n" + "="*60)
print("VERIFYING INTERCOMPANY CONFIGURATION ACROSS ALL COMPANIES")
print("="*60)

all_custs = get_all('Customer', ['name', 'customer_name', 'is_internal_customer', 'represents_company'])
all_supps = get_all('Supplier', ['name', 'supplier_name', 'is_internal_supplier', 'represents_company'])

int_cust_by_co = {c.get('represents_company'): c for c in all_custs if c.get('is_internal_customer')}
int_supp_by_co = {s.get('represents_company'): s for s in all_supps if s.get('is_internal_supplier')}

all_ok = True
for co in companies:
    cust = int_cust_by_co.get(co)
    supp = int_supp_by_co.get(co)
    
    cust_str = f"Customer: '{cust['name']}'" if cust else "MISSING CUSTOMER"
    supp_str = f"Supplier: '{supp['name']}'" if supp else "MISSING SUPPLIER"
    
    status = "OK" if (cust and supp) else "FAILED"
    if status == "FAILED":
        all_ok = False
    print(f"[{status}] Company: {co:<35} | {cust_str:<35} | {supp_str}")

print("\nIntercompany setup process complete! All OK:", all_ok)
