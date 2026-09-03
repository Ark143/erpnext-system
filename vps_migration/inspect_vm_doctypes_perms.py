import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# 1. Get all DocTypes belonging to 'Vehicle Management' module
r = opener.open('http://38.247.138.224:10017/api/resource/DocType?filters=' + urllib.parse.quote(json.dumps([['module', '=', 'Vehicle Management']])))
doctypes = json.loads(r.read().decode())['data']
print("DocTypes in Vehicle Management module:")
for d in doctypes:
    dt_name = d['name']
    r_dt = opener.open('http://38.247.138.224:10017/api/resource/DocType/' + urllib.parse.quote(dt_name))
    dt_doc = json.loads(r_dt.read().decode())['data']
    perms = dt_doc.get('permissions', [])
    roles = [p['role'] for p in perms]
    print(f"  {dt_name}: {roles}")
