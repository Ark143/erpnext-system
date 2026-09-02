import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def api_get(url):
    req = urllib.request.Request(url, headers=H)
    return json.loads(op.open(req).read().decode())

qs = urllib.parse.urlencode({
    'filters': json.dumps([['is_group', '=', 0]]),
    'fields': json.dumps(['name', 'warehouse_name', 'company']),
    'limit': 50
})
whs = api_get(f'http://38.247.138.224:10017/api/resource/Warehouse?{qs}').get('data', [])
print('Active Warehouses:')
for w in whs:
    print(f"  - {w['name']} ({w['company']})")
