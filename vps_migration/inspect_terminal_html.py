import urllib.request, urllib.parse, json, http.cookiejar, re

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

wp = json.loads(op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal', headers=H)).read().decode())
html = wp['data']['main_section_html']

print("HTML len:", len(html))
for m in re.finditer(r'jsQR', html):
    print("jsQR match:", html[max(0, m.start()-40):min(len(html), m.end()+60)])

for m in re.finditer(r'<script[^>]+src=["\']([^"\']+)["\']', html):
    print("script src:", m.group(1))

# Check inline libraries before POS
print("\nFirst 1500 chars of HTML:")
print(html[:1500])
