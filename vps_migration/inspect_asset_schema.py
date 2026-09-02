import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def get_doc(dt, name):
    r = op.open(urllib.request.Request(f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(dt)}/{urllib.parse.quote(name)}', headers=H))
    return json.loads(r.read().decode()).get('data', {})

# Inspect Asset DocType meta / fields
r_meta = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/DocType/Asset', headers=H))
meta = json.loads(r_meta.read().decode()).get('data', {})
fields = [f['fieldname'] for f in meta.get('fields', [])]
print('Asset fields:', [f for f in fields if 'deprec' in f or 'date' in f or 'book' in f or 'value' in f or 'amount' in f])

# Inspect Asset Category fields
r_ac_meta = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/DocType/Asset%20Category', headers=H))
ac_meta = json.loads(r_ac_meta.read().decode()).get('data', {})
ac_fields = [f['fieldname'] for f in ac_meta.get('fields', [])]
print('Asset Category fields:', ac_fields)
