import requests, json

s = requests.Session()
r = s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})
print('Login status:', r.status_code)

# Check Web Pages
wp = s.get('http://38.247.138.224:10017/api/resource/Web Page?fields=["name","title","route"]&limit_page_length=500').json()
print('Web Pages:', wp.get('data'))

# Check Pages
pages = s.get('http://38.247.138.224:10017/api/resource/Page?fields=["name","title","module"]&limit_page_length=500').json()
print('\nRelevant Pages:')
for p in pages.get('data', []):
    if any(k in p['name'].lower() for k in ['pos', 'vehicle', 'terminal']):
        print(' - Page:', p)

# Check Companies
comp = s.get('http://38.247.138.224:10017/api/resource/Company?fields=["name","abbr","default_currency"]&limit_page_length=100').json()
print('\nCompanies:', [c['name'] for c in comp.get('data', [])])

# Check POS Profiles
profiles = s.get('http://38.247.138.224:10017/api/resource/POS Profile?fields=["name","company","cost_center","warehouse"]&limit_page_length=100').json()
print('\nPOS Profiles:')
for p in profiles.get('data', []):
    print(' - Profile:', p)
