import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type':'application/x-www-form-urlencoded','X-Requested-With':'XMLHttpRequest','Accept':'application/json'}
data = urllib.parse.urlencode({'cmd':'login','usr':'administrator','pwd':'admin'}).encode()
op.open(urllib.request.Request(URL+'/api/method/login', data=data, headers=H), timeout=30)

def get_list(doctype):
    res = op.open(urllib.request.Request(f"{URL}/api/resource/{urllib.parse.quote(doctype)}?limit_page_length=200", headers=H))
    return json.loads(res.read().decode()).get('data', [])

print("=== EXISTING NUMBER CARDS ===")
for nc in get_list('Number Card'):
    print(" -", nc.get('name'))

print("\n=== EXISTING DASHBOARD CHARTS ===")
for dc in get_list('Dashboard Chart'):
    print(" -", dc.get('name'))

print("\n=== SAMPLE REPORTS ===")
reports = get_list('Report')
print(f"Total reports: {len(reports)}")
for r in reports[:40]:
    print(" -", r.get('name'))
