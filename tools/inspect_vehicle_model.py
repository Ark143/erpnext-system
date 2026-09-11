import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

# 1. Inspect all fields of ACC-SINV-2026-00449 that mention Toyota or INNOVA or Model
r = op.open(urllib.request.Request(f'{URL}/api/resource/Sales%20Invoice/ACC-SINV-2026-00449', headers=H))
inv = json.loads(r.read().decode()).get('data', {})
print("--- Sales Invoice relevant fields ---")
for k, v in inv.items():
    if v and ('model' in k.lower() or 'make' in k.lower() or 'veh' in k.lower() or 'toyota' in str(v).lower() or 'innova' in str(v).lower()):
        print(f"  {k}: {v}")

# 2. Check all Vehicle Models matching INNOVA or Toyota
r_vm = op.open(urllib.request.Request(f'{URL}/api/resource/Vehicle%20Model?limit_page_length=100', headers=H))
models = json.loads(r_vm.read().decode()).get('data', [])
print(f"\n--- Total Vehicle Models: {len(models)} ---")
innova_models = [m['name'] for m in models if 'innova' in m['name'].lower()]
print("Matching Innova models in DB:", innova_models)

# 3. Check Vehicle Makes
r_vmake = op.open(urllib.request.Request(f'{URL}/api/resource/Vehicle%20Make?limit_page_length=100', headers=H))
makes = json.loads(r_vmake.read().decode()).get('data', [])
print("\nVehicle Makes:", [m['name'] for m in makes])
