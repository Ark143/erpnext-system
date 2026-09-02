import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

try:
    r_call = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_test_exporter', headers=H))
    print(r_call.read().decode())
except urllib.error.HTTPError as e:
    print('CODE:', e.code)
    if e.fp:
        print('BODY:', e.fp.read().decode())
