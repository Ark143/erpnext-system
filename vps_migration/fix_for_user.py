import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

# Check for_user in Workspace Sidebar
res = op.open(urllib.request.Request(f'{URL}/api/resource/Workspace%20Sidebar/Vehicle%20Management', headers=H))
doc = json.loads(res.read().decode()).get('data', {})
print("Current for_user value in Workspace Sidebar:", repr(doc.get('for_user')))

# If for_user is "", set it to None / null in database or update it
req = urllib.request.Request(
    f"{URL}/api/resource/Workspace%20Sidebar/Vehicle%20Management",
    data=urllib.parse.urlencode({'data': json.dumps({"for_user": None})}).encode(),
    headers=H
)
req.get_method = lambda: 'PUT'
res = op.open(req)
print("Updated Workspace Sidebar with for_user=None, status:", res.status)
