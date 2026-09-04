import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

target_roles = ['System Manager', 'Desk User', 'Sales User', 'Sales Manager', 'Maintenance User', 'Maintenance Manager', 'Stock User', 'Stock Manager', 'Accounts User']

roles_child = [{'role': r} for r in target_roles]

payload = {
    'link_type': 'External',
    'link': '/desk/vehicle-management',
    'icon': 'car',
    'bg_color': 'blue',
    'hidden': 0,
    'roles': roles_child
}

url = 'http://38.247.138.224:10017/api/resource/Desktop%20Icon/Vehicle%20Management'
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=H, method='PUT')
res = opener.open(req)
print('Updated Desktop Icon/Vehicle Management: HTTP', res.status)

# Verify updated document
doc = json.loads(opener.open(url).read().decode())['data']
print('Updated Desktop Icon fields:')
print('  label:', doc.get('label'))
print('  link_type:', doc.get('link_type'))
print('  link:', doc.get('link'))
print('  icon:', doc.get('icon'))
print('  roles:', [r['role'] for r in doc.get('roles', [])])
