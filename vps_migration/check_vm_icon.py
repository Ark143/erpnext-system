import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# Get Desktop Icon for Vehicle Management
r = opener.open('http://38.247.138.224:10017/api/resource/Desktop%20Icon/Vehicle%20Management')
ic_data = json.loads(r.read().decode())['data']
print('Icon full data:')
for k, v in ic_data.items():
    if v or v == 0:
        print(' ', k, ':', repr(v))
