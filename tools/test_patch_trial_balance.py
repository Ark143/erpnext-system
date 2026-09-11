import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

probe_code = '''
# Inspect what is in frappe namespace
res = {}
for k in dir(frappe):
    if not k.startswith('_'):
        res[k] = str(type(getattr(frappe, k)))

frappe.response["message"] = res
'''

doc_name = "VM Patch Trial Balance"
req = urllib.request.Request(
    f"{URL}/api/resource/Server%20Script/{urllib.parse.quote(doc_name)}",
    data=urllib.parse.urlencode({'data': json.dumps({'script': probe_code})}).encode(),
    headers=H
)
req.get_method = lambda: 'PUT'
op.open(req)

try:
    res = op.open(urllib.request.Request(f"{URL}/api/method/vm_patch_trial_balance", headers=H))
    print("Probe output:", res.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTPError {e.code}:", e.read().decode())
