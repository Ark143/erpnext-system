import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# Update System Settings default_workspace to 'Vehicle Management'
ss_url = 'http://38.247.138.224:10017/api/resource/System%20Settings/System%20Settings'
payload = json.dumps({
    'default_workspace': 'Vehicle Management'
}).encode()
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
req = urllib.request.Request(ss_url, data=payload, headers=H, method='PUT')
res = opener.open(req)
print('Updated System Settings default_workspace: HTTP', res.status)

# Verify
doc = json.loads(opener.open(ss_url).read().decode())['data']
print('System Settings default_workspace is now:', doc.get('default_workspace'))
