import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# In Frappe Server Script, let's test if json is in namespace
script_code = """
frappe.response['message'] = {
    'json_loaded': json.loads('{"test": 123}')
}
"""

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote('Probe API'),
    data=json.dumps({'script': script_code}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)
opener.open(req)

try:
    r = opener.open('http://38.247.138.224:10017/api/method/vm_probe_api')
    print('RESPONSE:', r.read().decode())
except urllib.error.HTTPError as e:
    print('ERROR:', e.code, e.read().decode()[:500])
