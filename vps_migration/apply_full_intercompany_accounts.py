import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)
print("[OK] Logged in to ERPNext as Administrator", flush=True)

# 1. Update Debtors - MC and Creditors - MC account currency to PHP if needed
for acc_name in ['Debtors - MC', 'Creditors - MC']:
    r = session.put(f"{BASE_URL}/api/resource/Account/{requests.utils.quote(acc_name)}", json={'account_currency': 'PHP'}, timeout=30)
    print(f"Update {acc_name} currency to PHP: {r.status_code}", flush=True)

# 2. Fetch all companies and their default AR/AP accounts
comp_res = session.get(f"{BASE_URL}/api/resource/Company?fields=[\"name\",\"abbr\",\"default_receivable_account\",\"default_payable_account\"]&limit_page_length=100").json()
companies = comp_res.get('data', [])
company_names = [c['name'] for c in companies]
company_ar = {c['name']: c.get('default_receivable_account') for c in companies}
company_ap = {c['name']: c.get('default_payable_account') for c in companies}

allowed_companies_all = [{'company': co} for co in company_names]
customer_party_accounts = [{'company': co, 'account': company_ar[co]} for co in company_names if company_ar.get(co)]
supplier_party_accounts = [{'company': co, 'account': company_ap[co]} for co in company_names if company_ap.get(co)]

# 3. Update all internal customers with both allowed companies and party accounts
int_custs = session.get(f'{BASE_URL}/api/resource/Customer?filters=[["is_internal_customer","=",1]]&fields=["name","customer_name","represents_company"]&limit_page_length=200').json().get('data', [])

print(f"\nUpdating {len(int_custs)} Internal Customers...", flush=True)
for c in int_custs:
    doc_name = c['name']
    rep_company = c.get('represents_company')
    payload = {
        'is_internal_customer': 1,
        'represents_company': rep_company,
        'companies': allowed_companies_all,
        'accounts': customer_party_accounts
    }
    r = session.put(f"{BASE_URL}/api/resource/Customer/{requests.utils.quote(doc_name)}", json=payload, timeout=30)
    print(f"Customer '{doc_name}': {r.status_code}", flush=True)

# 4. Update all internal suppliers with both allowed companies and party accounts
int_supps = session.get(f'{BASE_URL}/api/resource/Supplier?filters=[["is_internal_supplier","=",1]]&fields=["name","supplier_name","represents_company"]&limit_page_length=200').json().get('data', [])

print(f"\nUpdating {len(int_supps)} Internal Suppliers...", flush=True)
for s in int_supps:
    doc_name = s['name']
    rep_company = s.get('represents_company')
    payload = {
        'is_internal_supplier': 1,
        'represents_company': rep_company,
        'companies': allowed_companies_all,
        'accounts': supplier_party_accounts
    }
    r = session.put(f"{BASE_URL}/api/resource/Supplier/{requests.utils.quote(doc_name)}", json=payload, timeout=30)
    print(f"Supplier '{doc_name}': {r.status_code}", flush=True)

print("\n" + "="*80, flush=True)
print("VERIFYING FULL 13x13 INTERCOMPANY INTERCONNECTIVITY", flush=True)
print("="*80, flush=True)

all_ok = True
for co in company_names:
    matching_cust = next((c for c in int_custs if c.get('represents_company') == co), None)
    matching_supp = next((s for s in int_supps if s.get('represents_company') == co), None)
    
    cust_doc = session.get(f"{BASE_URL}/api/resource/Customer/{requests.utils.quote(matching_cust['name'])}").json().get('data', {}) if matching_cust else {}
    supp_doc = session.get(f"{BASE_URL}/api/resource/Supplier/{requests.utils.quote(matching_supp['name'])}").json().get('data', {}) if matching_supp else {}
    
    cust_cos = len(cust_doc.get('companies', []))
    cust_accs = len(cust_doc.get('accounts', []))
    supp_cos = len(supp_doc.get('companies', []))
    supp_accs = len(supp_doc.get('accounts', []))
    
    print(f"[{'PASS' if cust_cos==13 and cust_accs==13 and supp_cos==13 and supp_accs==13 else 'FAIL'}] {co:<35} | Cust: {cust_cos} cos, {cust_accs} accs | Supp: {supp_cos} cos, {supp_accs} accs", flush=True)
    if not (cust_cos==13 and cust_accs==13 and supp_cos==13 and supp_accs==13):
        all_ok = False

print(f"\nFinal Complete Intercompany Matrix: 100% Configured: {all_ok}", flush=True)
