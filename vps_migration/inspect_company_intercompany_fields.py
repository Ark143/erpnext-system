import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'})

# 1. Inspect Company doctype fields
comp_meta = session.get(f"{BASE_URL}/api/method/frappe.desk.form.load.getdoctype?doctype=Company").json()
c_fields = comp_meta.get('docs', [{}])[0].get('fields', [])
int_comp_fields = [f for f in c_fields if any(k in f.get('fieldname', '').lower() for k in ['inter', 'internal', 'customer', 'supplier', 'transact'])]
print("=== COMPANY DOCTYPE INTERCOMPANY/CUSTOMER/SUPPLIER FIELDS ===")
for f in int_comp_fields:
    print(f"Field: {f['fieldname']} | Label: {f.get('label')} | Type: {f.get('fieldtype')} | Options: {f.get('options')}")

# 2. Inspect a sample Company record
comp_doc = session.get(f"{BASE_URL}/api/resource/Company/Ultra%20MRF%20Warehouse%20Dau").json()
print("\n=== SAMPLE COMPANY DOC (Ultra MRF Warehouse Dau) ===")
print(json.dumps(comp_doc.get('data', {}), indent=2))

# 3. Check Accounts of each Company (Receivable / Payable / COGS / Stock etc.)
print("\n=== ACCOUNTS PER COMPANY ===")
comp_res = session.get(f"{BASE_URL}/api/resource/Company?fields=[\"name\",\"default_receivable_account\",\"default_payable_account\",\"default_currency\"]&limit_page_length=100").json()
for c in comp_res.get('data', []):
    print(f"Company: {c['name']:<35} | AR: {str(c.get('default_receivable_account')):<35} | AP: {str(c.get('default_payable_account'))}")
