import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)
print("[OK] Logged in to ERPNext as Administrator", flush=True)

# 1. Fetch all companies and their default AR/AP accounts
comp_res = session.get(f"{BASE_URL}/api/resource/Company?fields=[\"name\",\"abbr\",\"default_receivable_account\",\"default_payable_account\"]&limit_page_length=100").json()
companies = comp_res.get('data', [])

company_names = [c['name'] for c in companies]
company_ar = {c['name']: c.get('default_receivable_account') for c in companies}
company_ap = {c['name']: c.get('default_payable_account') for c in companies}

print(f"Loaded {len(companies)} companies with AR/AP accounts:\n", flush=True)
for c in companies:
    print(f" - {c['name']:<35} | AR: {str(company_ar[c['name']]):<25} | AP: {str(company_ap[c['name']])}", flush=True)

# 2. Build full child tables for all 13 companies:
# (a) Allowed to Transact With (all 13 companies)
allowed_companies_all = [{'company': co} for co in company_names]

# (b) Party Accounts for Customer (all 13 companies with their respective Debtors account)
customer_party_accounts = [{'company': co, 'account': company_ar[co]} for co in company_names if company_ar.get(co)]

# (c) Party Accounts for Supplier (all 13 companies with their respective Creditors account)
supplier_party_accounts = [{'company': co, 'account': company_ap[co]} for co in company_names if company_ap.get(co)]

print(f"\nConstructed {len(allowed_companies_all)} allowed company entries, {len(customer_party_accounts)} customer party accounts, {len(supplier_party_accounts)} supplier party accounts.", flush=True)

# 3. Update all 13 Internal Customers
print("\n" + "="*70, flush=True)
print("UPDATING ALL 13 INTERNAL CUSTOMERS WITH ALL COMPANIES & ACCOUNTS", flush=True)
print("="*70, flush=True)

int_custs = session.get(f'{BASE_URL}/api/resource/Customer?filters=[["is_internal_customer","=",1]]&fields=["name","customer_name","represents_company"]&limit_page_length=200').json().get('data', [])

for c in int_custs:
    doc_name = c['name']
    rep_company = c.get('represents_company')
    print(f"Updating Customer '{doc_name}' (Represents: {rep_company})...", flush=True)
    
    payload = {
        'is_internal_customer': 1,
        'represents_company': rep_company,
        'companies': allowed_companies_all,
        'accounts': customer_party_accounts
    }
    
    r = session.put(f"{BASE_URL}/api/resource/Customer/{requests.utils.quote(doc_name)}", json=payload, timeout=30)
    if r.status_code == 200:
        print(f"  [OK] Successfully updated Customer '{doc_name}' with all 13 companies & accounts.", flush=True)
    else:
        print(f"  [ERROR] Updating '{doc_name}': {r.status_code} - {r.text}", flush=True)

# 4. Update all 13 Internal Suppliers
print("\n" + "="*70, flush=True)
print("UPDATING ALL 13 INTERNAL SUPPLIERS WITH ALL COMPANIES & ACCOUNTS", flush=True)
print("="*70, flush=True)

int_supps = session.get(f'{BASE_URL}/api/resource/Supplier?filters=[["is_internal_supplier","=",1]]&fields=["name","supplier_name","represents_company"]&limit_page_length=200').json().get('data', [])

for s in int_supps:
    doc_name = s['name']
    rep_company = s.get('represents_company')
    print(f"Updating Supplier '{doc_name}' (Represents: {rep_company})...", flush=True)
    
    payload = {
        'is_internal_supplier': 1,
        'represents_company': rep_company,
        'companies': allowed_companies_all,
        'accounts': supplier_party_accounts
    }
    
    r = session.put(f"{BASE_URL}/api/resource/Supplier/{requests.utils.quote(doc_name)}", json=payload, timeout=30)
    if r.status_code == 200:
        print(f"  [OK] Successfully updated Supplier '{doc_name}' with all 13 companies & accounts.", flush=True)
    else:
        print(f"  [ERROR] Updating '{doc_name}': {r.status_code} - {r.text}", flush=True)

print("\n" + "="*70, flush=True)
print("FINAL AUDIT AND VERIFICATION", flush=True)
print("="*70, flush=True)

all_ok = True
for co in company_names:
    # Check customer
    matching_cust = next((c for c in int_custs if c.get('represents_company') == co), None)
    # Check supplier
    matching_supp = next((s for s in int_supps if s.get('represents_company') == co), None)
    
    if matching_cust:
        cust_doc = session.get(f"{BASE_URL}/api/resource/Customer/{requests.utils.quote(matching_cust['name'])}").json().get('data', {})
        cust_cos = len(cust_doc.get('companies', []))
        cust_accs = len(cust_doc.get('accounts', []))
    else:
        cust_cos, cust_accs = 0, 0

    if matching_supp:
        supp_doc = session.get(f"{BASE_URL}/api/resource/Supplier/{requests.utils.quote(matching_supp['name'])}").json().get('data', {})
        supp_cos = len(supp_doc.get('companies', []))
        supp_accs = len(supp_doc.get('accounts', []))
    else:
        supp_cos, supp_accs = 0, 0
        
    print(f"Company: {co:<35} | Cust '{matching_cust['name'] if matching_cust else 'NONE'}': {cust_cos} cos, {cust_accs} accs | Supp '{matching_supp['name'] if matching_supp else 'NONE'}': {supp_cos} cos, {supp_accs} accs", flush=True)
    
    if cust_cos < 13 or cust_accs < 13 or supp_cos < 13 or supp_accs < 13:
        all_ok = False

print(f"\nAll 13 companies fully configured and interconnected: {all_ok}", flush=True)
