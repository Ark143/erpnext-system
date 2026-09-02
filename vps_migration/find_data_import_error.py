import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

# We can create a Server Script to test Exporter on all DocTypes and pinpoint the exact error!
test_script = '''
def test_export():
    import frappe
    from frappe.core.doctype.data_import.exporter import Exporter

    doctypes = [d.name for d in frappe.get_all("DocType", filters={"istable": 0, "issingle": 0})]
    problematic = []

    for dt in doctypes:
        try:
            e = Exporter(dt, export_fields={}, export_data=False)
        except Exception as ex:
            problematic.append({"doctype": dt, "error": str(ex)})

    frappe.response["message"] = problematic

test_export()
'''

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Test%20Exporter',
    data=urllib.parse.urlencode({'data': json.dumps({
        'name': 'VM Test Exporter',
        'doctype': 'Server Script',
        'script_type': 'API',
        'api_method': 'vm_test_exporter',
        'allow_guest': 1,
        'disabled': 0,
        'script': test_script
    })}).encode(),
    headers=H
)
try:
    op.open(req)
except Exception:
    pass

r_call = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_test_exporter', headers=H))
res = json.loads(r_call.read().decode())
print("Problematic DocTypes for Exporter / Data Import:")
print(json.dumps(res.get('message', []), indent=2))
