import urllib.request, urllib.parse, json, http.cookiejar, re

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Web%20Page/vm-company-dashboard', headers=H))
doc = json.loads(r.read().decode())['data']
html = doc.get('main_section_html') or ''

print('approvals in vm-company-dashboard:', 'approval' in html.lower())
for m in re.finditer(r'href=[\'"][^\'"]+[\'"]', html):
    print('HREF:', m.group(0))

for m in re.finditer(r'(?:window\.open|location\.href)[^;\n]+', html):
    print('JS NAV:', m.group(0))
