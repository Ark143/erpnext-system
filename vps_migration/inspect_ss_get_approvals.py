import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Server%20Script/Executive%20Dashboard%20API', headers=H))
doc = json.loads(r.read().decode())['data']
script = doc['script']

# Find def get_approvals
idx = script.find('def get_approvals():')
end_idx = script.find('def get_operations():', idx)
print("Current get_approvals body:")
print(script[idx:end_idx])
