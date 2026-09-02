import urllib.request, urllib.parse, json, http.cookiejar, re

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def api_get(url):
    req = urllib.request.Request(url, headers=H)
    return json.loads(op.open(req).read().decode())

wp_list = api_get('http://38.247.138.224:10017/api/resource/Web%20Page?limit_page_length=100').get('data', [])
matching_pages = []

for wp in wp_list:
    name = wp['name']
    r = op.open(urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Web%20Page/{urllib.parse.quote(name)}', headers=H))
    doc = json.loads(r.read().decode())['data']
    html = doc.get('main_section_html') or ''
    has_openlist = 'openlist' in html.lower()
    has_approvals = 'approvalcards' in html.lower()
    if has_openlist or has_approvals:
        matching_pages.append(name)
        print(f"Found match in Web Page: {name} (openList: {has_openlist}, approvalCards: {has_approvals})")

print(f"\nTotal matching pages: {len(matching_pages)}")
