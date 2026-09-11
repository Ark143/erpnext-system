import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

res = op.open(urllib.request.Request(f'{URL}/api/resource/Server%20Script?fields=["name","script_type","reference_doctype","api_method","disabled"]&limit_page_length=100', headers=H))
scripts = json.loads(res.read().decode()).get('data', [])
for s in scripts:
    print(s)
