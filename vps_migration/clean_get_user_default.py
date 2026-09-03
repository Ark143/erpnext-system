import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

for name in ['VM POS Open Shift', 'VM POS Create Invoice']:
    r = opener.open('http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote(name))
    d = json.loads(r.read().decode())['data']
    script = d['script']
    new_script = script.replace("frappe.defaults.get_user_default('Company')", "None")
    new_script = new_script.replace('frappe.defaults.get_user_default("Company")', "None")
    req = urllib.request.Request(
        'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote(name),
        data=json.dumps({'script': new_script}).encode(),
        headers={'Content-Type': 'application/json'},
        method='PUT'
    )
    opener.open(req)
    print(f'Cleaned {name}.')
