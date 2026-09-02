import urllib.request, urllib.parse, json, http.cookiejar, re

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Web%20Page/executive-dashboard', headers=H))
doc = json.loads(r.read().decode())['data']
html = doc.get('main_section_html') or ''

print("=== Search for href or open in executive-dashboard ===")
matches = re.findall(r'.{0,50}(?:href|window\.open|view|transaction|approv).{0,50}', html, re.IGNORECASE)
for m in matches[:30]:
    print("MATCH:", m.strip().replace('\n', ' '))
