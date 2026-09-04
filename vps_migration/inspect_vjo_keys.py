import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

res = op.open(urllib.request.Request(f"{URL}/api/resource/Vehicle%20Job%20Order?limit_page_length=1", headers=H))
doc_meta = json.loads(res.read().decode())
print("VJO list:", doc_meta)

name = doc_meta['data'][0]['name']
res2 = op.open(urllib.request.Request(f"{URL}/api/resource/Vehicle%20Job%20Order/{name}", headers=H))
vjo_doc = json.loads(res2.read().decode()).get('data', {})
print("VJO keys:", list(vjo_doc.keys()))
