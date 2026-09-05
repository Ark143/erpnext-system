import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
res = s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})
print("Login status:", res.status_code)

# 1. POS Profiles
pos_profiles = s.get(f'{URL}/api/resource/POS Profile', params={'fields': json.dumps(['name','company','warehouse','disabled']), 'limit_page_length': 100}).json()
print("\n--- POS Profiles ---")
for p in pos_profiles.get('data', []):
    print(p)

# 2. Open Entries
open_entries = s.get(f'{URL}/api/resource/POS Opening Entry', params={'fields': json.dumps(['name','pos_profile','user','company','status','docstatus','posting_date']), 'filters': json.dumps([['docstatus','=',1],['status','=','Open']]), 'limit_page_length': 100}).json()
print("\n--- Open POS Entries ---")
for o in open_entries.get('data', []):
    print(o)

# 3. Server scripts related to POS
scripts = s.get(f'{URL}/api/resource/Server Script', params={'fields': json.dumps(['name','script_type','api_method','disabled']), 'limit_page_length': 100}).json()
print("\n--- POS / VM Server Scripts ---")
for sc in scripts.get('data', []):
    name = sc.get('name', '')
    api = sc.get('api_method') or ''
    if 'pos' in name.lower() or 'pos' in api.lower() or 'vm' in name.lower():
        print(sc)
