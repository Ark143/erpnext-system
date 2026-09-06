import requests, json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# 1. Customer Groups & Territories
cg = s.get('http://38.247.138.224:10017/api/resource/Customer Group?fields=["name"]&limit_page_length=50').json()
print("Customer Groups:", [x['name'] for x in cg.get('data', [])])

sg = s.get('http://38.247.138.224:10017/api/resource/Supplier Group?fields=["name"]&limit_page_length=50').json()
print("Supplier Groups:", [x['name'] for x in sg.get('data', [])])

terr = s.get('http://38.247.138.224:10017/api/resource/Territory?fields=["name"]&limit_page_length=50').json()
print("Territories:", [x['name'] for x in terr.get('data', [])])

# 2. Inspect existing ULTRA MRF WAREHOUSE DAU supplier
supp = s.get('http://38.247.138.224:10017/api/resource/Supplier/ULTRA MRF WAREHOUSE DAU').json()
print("\nSupplier 'ULTRA MRF WAREHOUSE DAU':")
print(json.dumps(supp.get('data', {}), indent=2))

# 3. Check existing customers
cust_list = s.get('http://38.247.138.224:10017/api/resource/Customer?fields=["name","customer_name","represents_company","is_internal_customer"]&limit_page_length=100').json()
print("\nSample Customers:")
for c in cust_list.get('data', [])[:10]:
    print(c)
