import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Fetch all companies
companies_res = s.get('http://38.247.138.224:10017/api/resource/Company?fields=["name","abbr"]&limit_page_length=100').json()
companies = [c['name'] for c in companies_res.get('data', [])]
print(f"Total Companies: {len(companies)}\n")

# Check existing Customers matching company names
for company in companies:
    cust_res = s.get(f'http://38.247.138.224:10017/api/resource/Customer?filters=[["customer_name","=","{requests.utils.quote(company)}"]]&fields=["name","customer_name","is_internal_customer","represents_company"]').json()
    cust_data = cust_res.get('data', [])
    
    supp_res = s.get(f'http://38.247.138.224:10017/api/resource/Supplier?filters=[["supplier_name","=","{requests.utils.quote(company)}"]]&fields=["name","supplier_name","is_internal_supplier","represents_company"]').json()
    supp_data = supp_res.get('data', [])
    
    print(f"Company: {company}")
    print(f"  Existing Customer: {cust_data}")
    print(f"  Existing Supplier: {supp_data}")
