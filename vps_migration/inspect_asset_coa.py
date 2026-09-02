import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def get_list(dt, filters=None, fields=None, limit=200):
    qs_dict = {'limit': limit}
    if filters: qs_dict['filters'] = json.dumps(filters)
    if fields: qs_dict['fields'] = json.dumps(fields)
    qs = urllib.parse.urlencode(qs_dict)
    r = op.open(urllib.request.Request(f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(dt)}?{qs}', headers=H))
    return json.loads(r.read().decode()).get('data', [])

# Check default company in Global Defaults
r_gd = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Global%20Defaults/Global%20Defaults', headers=H))
gd = json.loads(r_gd.read().decode()).get('data', {})
default_company = gd.get('default_company') or 'Ultra MRF Dau Main'
print('DEFAULT COMPANY:', default_company)

# Accounts for default company
accs = get_list('Account', filters=[['company', '=', default_company]], fields=['name', 'account_name', 'account_type', 'root_type', 'is_group'])
print(f"\n--- Relevant Accounts in {default_company} ---")
for a in accs:
    aname = a['name'].lower()
    atype = a.get('account_type') or ''
    if atype in ['Fixed Asset', 'Accumulated Depreciation', 'Depreciation', 'Expenses Included In Asset Valuation'] or 'asset' in aname or 'deprec' in aname:
        print(f"  {a['name']} | Type: {atype} | Root: {a.get('root_type')}")

# Cost Center
ccs = get_list('Cost Center', filters=[['company', '=', default_company]], fields=['name', 'is_group'])
print(f"\n--- Cost Centers in {default_company} ---")
for cc in ccs:
    print(f"  {cc['name']} (is_group: {cc.get('is_group')})")

# Locations
locs = get_list('Location', fields=['name'])
print(f"\n--- Locations ---")
for l in locs:
    print(f"  {l['name']}")
