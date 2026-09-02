import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def api_get(url):
    req = urllib.request.Request(url, headers=H)
    return json.loads(op.open(req).read().decode())

print('=== COMPANIES IN POS TERMINAL ===')
meta = api_get('http://38.247.138.224:10017/api/method/vehicle_management.vehicle_management.pos_api.get_meta')
companies = meta.get('message', {}).get('companies', [])
print('Companies count:', len(companies))
for c in companies:
    print(' -', c)

print('\n=== POS PROFILES ===')
profiles = api_get('http://38.247.138.224:10017/api/resource/POS%20Profile?limit=50').get('data', [])
for p in profiles:
    doc = api_get('http://38.247.138.224:10017/api/resource/POS%20Profile/' + urllib.parse.quote(p['name'])).get('data', {})
    print(f"Profile: {doc['name']} | Company: {doc.get('company')} | Warehouse: {doc.get('warehouse')}")
