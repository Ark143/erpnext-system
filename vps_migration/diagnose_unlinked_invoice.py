import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

script_diag = '''
def diagnose():
    import frappe
    doc = frappe.get_doc("Vehicle POS Invoice", "VMSPOS-2026-00007")
    try:
        doc.create_erpnext_pos_invoice()
        frappe.db.commit()
        frappe.response["message"] = {"status": "success", "pos_invoice": doc.pos_invoice}
    except Exception as e:
        frappe.response["message"] = {"status": "error", "error": str(e), "traceback": frappe.get_traceback()}

diagnose()
'''

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Diagnose%20Sync',
    data=urllib.parse.urlencode({'data': json.dumps({
        'name': 'VM Diagnose Sync',
        'doctype': 'Server Script',
        'script_type': 'API',
        'api_method': 'vm_diagnose_sync',
        'allow_guest': 1,
        'disabled': 0,
        'script': script_diag
    })}).encode(),
    headers=H
)
try:
    op.open(req)
except Exception:
    req.get_method = lambda: 'PUT'
    op.open(req)

r_call = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_diagnose_sync', headers=H))
print("Diagnosis Response:")
print(r_call.read().decode())
