import requests, json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# 1. Get all companies
comp_res = s.get('http://38.247.138.224:10017/api/resource/Company?fields=["name","abbr","default_currency","default_receivable_account","default_payable_account"]&limit_page_length=100').json()
companies = comp_res.get('data', [])
print('=== COMPANIES ===')
for c in companies:
    print(f" - {c['name']} (Abbr: {c.get('abbr')})")

# 2. Check Customer fields related to internal customer
cust_meta = s.get('http://38.247.138.224:10017/api/method/frappe.desk.form.load.getdoctype?doctype=Customer').json()
fields = cust_meta.get('docs', [{}])[0].get('fields', [])
int_cust_fields = [f['fieldname'] for f in fields if any(k in f['fieldname'].lower() for k in ['internal', 'company', 'represents', 'supplier'])]
print('\n=== CUSTOMER INTERNAL FIELDS ===', int_cust_fields)

# 3. Check Supplier fields related to internal supplier
supp_meta = s.get('http://38.247.138.224:10017/api/method/frappe.desk.form.load.getdoctype?doctype=Supplier').json()
s_fields = supp_meta.get('docs', [{}])[0].get('fields', [])
int_supp_fields = [f['fieldname'] for f in s_fields if any(k in f['fieldname'].lower() for k in ['internal', 'company', 'represents', 'customer'])]
print('\n=== SUPPLIER INTERNAL FIELDS ===', int_supp_fields)

# 4. Check existing internal customers and suppliers
int_custs = s.get('http://38.247.138.224:10017/api/resource/Customer?filters=[["is_internal_customer","=",1]]&fields=["name","customer_name","represents_company"]&limit_page_length=100').json()
print('\n=== EXISTING INTERNAL CUSTOMERS ===', int_custs.get('data', []))

int_supps = s.get('http://38.247.138.224:10017/api/resource/Supplier?filters=[["is_internal_supplier","=",1]]&fields=["name","supplier_name","represents_company"]&limit_page_length=100').json()
print('\n=== EXISTING INTERNAL SUPPLIERS ===', int_supps.get('data', []))
