import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

script_test = '''
def test_sync():
    import frappe
    doc = frappe.get_doc("Vehicle POS Invoice", "VMSPOS-2026-00007")
    try:
        doc.create_erpnext_pos_invoice()
        frappe.response["message"] = {"success": True, "pos_invoice": doc.pos_invoice}
    except Exception as e:
        frappe.response["message"] = {"success": False, "error": str(e), "tb": frappe.get_traceback()}

test_sync()
'''

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Test%20POS%20Sync',
    data=urllib.parse.urlencode({'data': json.dumps({
        'name': 'VM Test POS Sync',
        'doctype': 'Server Script',
        'script_type': 'API',
        'api_method': 'vm_test_pos_sync',
        'allow_guest': 1,
        'disabled': 0,
        'script': script_test
    })}).encode(),
    headers=H
)
try:
    op.open(req)
except Exception:
    pass

r_call = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_test_pos_sync', headers=H))
res = json.loads(r_call.read().decode())
print("Sync Test Result:")
print(json.dumps(res, indent=2))
