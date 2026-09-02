import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def save_doc(doctype, name, doc_data):
    try:
        r = op.open(urllib.request.Request(f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(doctype)}/{urllib.parse.quote(name)}', headers=H))
        print(f"Updating existing {doctype} '{name}'...")
        req = urllib.request.Request(
            f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(doctype)}/{urllib.parse.quote(name)}',
            data=urllib.parse.urlencode({'data': json.dumps(doc_data)}).encode(),
            headers=H
        )
        req.get_method = lambda: 'PUT'
        res = op.open(req)
        print(f"Updated {doctype} '{name}'")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Creating new {doctype} '{name}'...")
            payload = dict(doc_data)
            payload['name'] = name
            payload['doctype'] = doctype
            req = urllib.request.Request(
                f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(doctype)}',
                data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(),
                headers=H
            )
            op.open(req)
            print(f"Created {doctype} '{name}'")
        else:
            raise

script_content = '''
def process_depreciation():
    # 1. Inspect Assets
    assets = frappe.get_all(
        "Asset",
        fields=["name", "asset_name", "item_code", "gross_purchase_amount", "value_after_depreciation", "status", "docstatus"],
        order_by="creation desc",
        limit=20
    )
    
    # 2. Inspect Depreciation Schedules
    schedules = frappe.get_all(
        "Asset Depreciation Schedule",
        fields=["name", "asset", "docstatus", "status"],
        order_by="creation desc",
        limit=20
    )
    
    # 3. Inspect Journal Entries
    jes = frappe.get_all(
        "Journal Entry",
        filters={"voucher_type": "Depreciation Entry"},
        fields=["name", "posting_date", "total_debit", "company", "user_remark"],
        order_by="creation desc",
        limit=50
    )
    
    frappe.response["message"] = {
        "status": "success",
        "assets_count": len(assets),
        "assets": assets[:10],
        "schedules_count": len(schedules),
        "schedules": schedules[:10],
        "journal_entries_count": len(jes),
        "journal_entries": jes
    }

process_depreciation()
'''

save_doc("Server Script", "VM Check Assets and Schedules", {
    "script_type": "API",
    "api_method": "vm_check_assets_and_schedules",
    "allow_guest": 1,
    "disabled": 0,
    "script": script_content
})

r_call = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_check_assets_and_schedules', headers=H))
res = json.loads(r_call.read().decode())
print("\n=== CURRENT ASSETS & DEPRECIATION SCHEDULE SUMMARY ===")
print(json.dumps(res.get('message', {}), indent=2))
