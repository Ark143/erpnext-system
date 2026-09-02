import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

script_sync_all = """
def sync_all_unlinked():
    unlinked = frappe.get_all(
        "Vehicle POS Invoice",
        filters={"docstatus": 1, "pos_invoice": ["in", ["", None]]},
        fields=["name", "company", "customer", "paid_amount", "total_amount"]
    )
    
    results = []
    for row in unlinked:
        name = row.name
        doc = frappe.get_doc("Vehicle POS Invoice", name)
        try:
            doc.create_erpnext_pos_invoice()
            frappe.db.commit()
            results.append({"name": name, "status": "synced", "pos_invoice": doc.pos_invoice})
        except Exception as e:
            frappe.db.rollback()
            results.append({"name": name, "status": "error", "error": str(e)})
            
    frappe.response["message"] = {
        "unlinked_found": len(unlinked),
        "results": results
    }

sync_all_unlinked()
"""

name = 'VM Sync All Unlinked'
req = urllib.request.Request(
    f'http://38.247.138.224:10017/api/resource/Server%20Script/{urllib.parse.quote(name)}',
    data=urllib.parse.urlencode({'data': json.dumps({'script': script_sync_all})}).encode(),
    headers=H
)
req.get_method = lambda: 'PUT'
op.open(req)

r_call = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_sync_all_unlinked', headers=H))
print('Sync All Result:')
print(r_call.read().decode())
