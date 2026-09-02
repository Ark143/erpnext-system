import urllib.request, urllib.parse, json, http.cookiejar, re

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Web%20Page/executive-dashboard', headers=H))
doc = json.loads(r.read().decode())['data']
html = doc.get('main_section_html') or ''

print("=== Search for window.open ===")
for m in re.finditer(r'window\.open\([^)]+\)', html):
    print("  WINDOW.OPEN:", m.group(0))

print("\n=== Search for /desk links ===")
for m in re.finditer(r'[\'"][^\'"]*\/desk[^\'"]*[\'"]', html):
    print("  DESK LINK:", m.group(0))

print("\n=== Search for openList ===")
for m in re.finditer(r'.{0,40}openList.{0,40}', html):
    print("  OPENLIST:", m.group(0).strip())
