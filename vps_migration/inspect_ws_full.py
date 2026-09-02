import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Workspace/Vehicle%20Management', headers=H))
ws = json.loads(r.read().decode())['data']
print("=== SHORTCUTS ===")
print(json.dumps(ws.get('shortcuts', []), indent=2))
print("=== LINKS ===")
print(json.dumps(ws.get('links', []), indent=2))
print("=== CHARTS ===")
print(json.dumps(ws.get('charts', []), indent=2))
print("=== CONTENT ===")
try:
    print(json.dumps(json.loads(ws.get('content') or '[]'), indent=2))
except Exception:
    print(ws.get('content'))
