import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

res = op.open(urllib.request.Request(f'{URL}/api/resource/Workspace%20Sidebar/Vehicle%20Management', headers=H))
doc = json.loads(res.read().decode()).get('data', {})
print("Sidebar Doc Items Count in DB:", len(doc.get('items', [])))
for i, it in enumerate(doc.get('items', [])):
    print(f" {i+1}. label={it.get('label')} | type={it.get('type')} | link_to={it.get('link_to')}")
