import urllib.request, urllib.parse, json, http.cookiejar, re

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

pages = [
    'executive', 'executive-dashboard', 'executive-automan-car-care-center',
    'executive-san-fernando-warehouse', 'executive-the-wheelhub', 'executive-ultra-mrf',
    'executive-ultra-mrf-dau-annex', 'executive-ultra-mrf-dau-main',
    'executive-ultra-mrf-mexico-warehouse', 'executive-ultra-mrf-san-fernando',
    'executive-ultra-mrf-telebastagan', 'executive-ultra-mrf-telebastagan-2',
    'executive-ultra-mrf-warehouse-dau', 'executive-wheel-core'
]

for p in pages:
    r = op.open(urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Web%20Page/{p}', headers=H))
    doc = json.loads(r.read().decode())['data']
    html = doc.get('main_section_html') or ''
    idx = html.find('function openList')
    snippet = html[idx:idx+250] if idx != -1 else "NOT FOUND"
    print(f"Page: {p} | openList snippet: {repr(snippet[:120])}")
