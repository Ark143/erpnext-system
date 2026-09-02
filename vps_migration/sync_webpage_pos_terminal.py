import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

html_content = open(r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\www\pos_terminal.html', encoding='utf-8').read()

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal',
    data=urllib.parse.urlencode({'data': json.dumps({'main_section_html': html_content})}).encode(),
    headers=H
)
req.get_method = lambda: 'PUT'
res = op.open(req)
print('Updated Web Page vehicle-pos-terminal successfully! Status:', res.status)
