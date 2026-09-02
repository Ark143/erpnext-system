import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def api_get(url):
    req = urllib.request.Request(url, headers=H)
    return json.loads(op.open(req).read().decode()).get('data', [])

print("=== Reports related to Vehicle or POS ===")
reps = api_get('http://38.247.138.224:10017/api/resource/Report?limit_page_length=200')
for r in reps:
    name = r['name']
    if any(k in name.lower() for k in ['vehicle', 'pos', 'job', 'stock balance', 'sales invoice']):
        print(' - Report:', name)

print("\n=== Dashboard Charts ===")
charts = api_get('http://38.247.138.224:10017/api/resource/Dashboard%20Chart?limit_page_length=200')
for c in charts:
    name = c['name']
    if any(k in name.lower() for k in ['vehicle', 'pos', 'sales', 'job', 'revenue']):
        print(' - Chart:', name)

print("\n=== Number Cards ===")
ncards = api_get('http://38.247.138.224:10017/api/resource/Number%20Card?limit_page_length=200')
for n in ncards:
    name = n['name']
    if any(k in name.lower() for k in ['vehicle', 'pos', 'sales', 'job', 'revenue', 'order', 'customer']):
        print(' - Number Card:', name)
