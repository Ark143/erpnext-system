import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

fields = json.dumps(['name', 'email', 'enabled', 'user_type', 'full_name'])
r = opener.open('http://38.247.138.224:10017/api/resource/User?fields=' + urllib.parse.quote(fields) + '&limit_page_length=50')
users = json.loads(r.read().decode())['data']
for u in users:
    if u['name'] in ['Guest', 'Administrator']:
        continue
    r_u = opener.open('http://38.247.138.224:10017/api/resource/User/' + urllib.parse.quote(u['name']))
    u_data = json.loads(r_u.read().decode())['data']
    roles = [role['role'] for role in u_data.get('roles', [])]
    print("User:", u['name'], "(", u.get('full_name'), ") enabled=", u['enabled'])
    print("  Roles:", roles)
