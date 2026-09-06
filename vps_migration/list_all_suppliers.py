import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Fetch all suppliers
supp_res = s.get('http://38.247.138.224:10017/api/resource/Supplier?fields=["name","supplier_name","is_internal_supplier","represents_company"]&limit_page_length=500').json()
print(f"=== ALL SUPPLIERS ({len(supp_res.get('data', []))}) ===")
for sup in supp_res.get('data', []):
    print(sup)
