import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

for name in ['executive-dashboard', 'executive', 'vm-dashboard', 'vm-company-dashboard', 'executive-ultra-mrf']:
    try:
        r = op.open(urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Web%20Page/{name}', headers=H))
        doc = json.loads(r.read().decode())['data']
        html = doc.get('main_section_html') or ''
        print(f'=== {name} (len: {len(html)}) ===')
        for word in ['approval', 'approvals', 'view', 'transaction', '/app/']:
            cnt = html.lower().count(word)
            print(f'  count of "{word}": {cnt}')
    except Exception as e:
        print(f'=== {name} ERROR: {e} ===')
