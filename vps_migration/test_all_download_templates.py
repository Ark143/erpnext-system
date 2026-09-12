import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
res = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

# Test download_template on all key doctypes with specific export fields
doctypes_to_test = [
    ('Item', {'Item': ['item_code', 'item_name', 'item_group', 'stock_uom']}),
    ('Customer Vehicle', {'Customer Vehicle': ['plate_no', 'customer', 'vehicle_make', 'vehicle_model']}),
    ('Supplier', {'Supplier': ['supplier_name', 'supplier_group']}),
    ('Batch', {'Batch': ['batch_id', 'item']}),
    ('Bank Transaction', {'Bank Transaction': ['date', 'bank_account', 'deposit', 'withdrawal']}),
    ('Bank Statement Import Log', {}),
    ('Buying Settings', {}),
    ('Sales Invoice', {'Sales Invoice': ['customer', 'company', 'posting_date']}),
    ('Purchase Invoice', {'Purchase Invoice': ['supplier', 'company', 'posting_date']}),
    ('Payment Entry', {'Payment Entry': ['payment_type', 'party_type', 'party', 'paid_amount']}),
    ('Customer', {'Customer': ['customer_name', 'customer_type']})
]

print("Testing download_template across all DocTypes...")
all_passed = True
for dt, fields in doctypes_to_test:
    try:
        url = f'http://38.247.138.224:10017/api/method/frappe.core.doctype.data_import.data_import.download_template?doctype={urllib.parse.quote(dt)}&export_fields={urllib.parse.quote(json.dumps(fields))}&export_records=blank_template&file_type=CSV'
        req = urllib.request.Request(url, headers=H)
        resp = op.open(req)
        content = resp.read()
        print(f"[PASS] {dt}: HTTP {resp.status}, downloaded {len(content)} bytes")
    except urllib.error.HTTPError as e:
        all_passed = False
        print(f"[FAIL] {dt}: HTTP Error {e.code}: {e.read().decode()[:200]}")

if all_passed:
    print("\nSUCCESS: ALL DATA IMPORT TEMPLATES DOWNLOADED SUCCESSFULLY WITHOUT ERRORS!")
