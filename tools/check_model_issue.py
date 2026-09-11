import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

# Check DocTypes
for dt in ['Vehicle Model', 'Model', 'Vehicle Make', 'Make', 'Customer Vehicle', 'Sales Invoice']:
    try:
        r = op.open(urllib.request.Request(f'{URL}/api/resource/{urllib.parse.quote(dt)}?limit_page_length=5', headers=H))
        data = json.loads(r.read().decode()).get('data', [])
        print(f'{dt} exists! count >= {len(data)}')
    except Exception as e:
        print(f'{dt} error: {e}')

# Inspect ACC-SINV-2026-00449
try:
    r = op.open(urllib.request.Request(f'{URL}/api/resource/Sales%20Invoice/ACC-SINV-2026-00449', headers=H))
    inv = json.loads(r.read().decode()).get('data', {})
    print("\n--- Sales Invoice ACC-SINV-2026-00449 ---")
    for k in ['name', 'customer', 'vehicle', 'model', 'vehicle_model', 'make', 'docstatus']:
        if k in inv:
            print(f"{k}: {inv.get(k)}")
except Exception as e:
    print(f"Error reading Sales Invoice: {e}")
