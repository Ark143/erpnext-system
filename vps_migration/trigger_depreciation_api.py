import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

script_content = '''
def process_depreciation():
    import frappe
    from erpnext.assets.doctype.asset.depreciation import post_depreciation_entries
    
    # 1. Trigger post_depreciation_entries for current date
    post_depreciation_entries("2026-09-02")
    
    # 2. Query all booked Depreciation Journal Entries
    jes = frappe.get_all(
        "Journal Entry",
        filters={"voucher_type": "Depreciation Entry", "docstatus": 1},
        fields=["name", "posting_date", "total_debit", "company", "user_remark"],
        order_by="creation desc",
        limit=100
    )
    
    # 3. Query all 10 Assets and their updated book values
    assets = frappe.get_all(
        "Asset",
        fields=["name", "asset_name", "item_code", "gross_purchase_amount", "value_after_depreciation", "status"],
        order_by="creation desc",
        limit=10
    )
    
    frappe.response["message"] = {
        "status": "success",
        "posted_journal_entries_count": len(jes),
        "journal_entries": jes,
        "assets": assets
    }

process_depreciation()
'''

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Process%20Depreciation',
    data=urllib.parse.urlencode({'data': json.dumps({
        'name': 'VM Process Depreciation',
        'doctype': 'Server Script',
        'script_type': 'API',
        'api_method': 'vm_process_depreciation',
        'allow_guest': 1,
        'disabled': 0,
        'script': script_content
    })}).encode(),
    headers=H
)
try:
    op.open(req)
    print("Created/Updated Server Script 'VM Process Depreciation'")
except urllib.error.HTTPError as e:
    req.get_method = lambda: 'PUT'
    op.open(req)
    print("Updated Server Script 'VM Process Depreciation'")

try:
    r_call = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_process_depreciation', headers=H))
    res = json.loads(r_call.read().decode())
    print("\nAPI Response:")
    print(json.dumps(res, indent=2))
except urllib.error.HTTPError as e:
    print('ERR CODE:', e.code)
    if e.fp:
        print(e.fp.read().decode())
