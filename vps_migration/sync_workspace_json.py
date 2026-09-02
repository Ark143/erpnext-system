import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Workspace/Vehicle%20Management', headers=H))
ws_data = json.loads(r.read().decode())['data']

target_path = r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\vehicle_management\workspace\vehicle_management\vehicle_management.json'
with open(target_path, 'w', encoding='utf-8') as f:
    json.dump(ws_data, f, indent=1, ensure_ascii=False)

print("Saved synced workspace to", target_path)
