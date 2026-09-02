import urllib.request, urllib.parse, json, http.cookiejar, re

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Web%20Page/executive-dashboard', headers=H))
doc = json.loads(r.read().decode())['data']
html = doc.get('main_section_html') or ''

matches = [m.start() for m in re.finditer(r'approvalCards', html)]
print("Indices of approvalCards:", matches)
for m in matches:
    if m > 35000: # in JS script
        print("=== JS around idx", m, "===")
        print(html[m-100:m+2000])
