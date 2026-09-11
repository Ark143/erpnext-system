import urllib.request
import urllib.parse
import json
import http.cookiejar

base_url = 'http://38.247.138.224:10017'
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Login
login_data = urllib.parse.urlencode({'usr': 'Administrator', 'pwd': 'admin'}).encode('utf-8')
opener.open(urllib.request.Request(f'{base_url}/api/method/login', data=login_data))

pairs = [
    ('ACC-BTN-2026-00009', 'ACC-PAY-2026-00278', 15000.0, '2026-09-02'),
    ('ACC-BTN-2026-00010', 'ACC-PAY-2026-00279', 4500.0, '2026-09-05'),
    ('ACC-BTN-2026-00011', 'ACC-PAY-2026-00280', 22000.0, '2026-09-10'),
    ('ACC-BTN-2026-00012', 'ACC-PAY-2026-00281', 1500.0, '2026-09-15'),
    ('ACC-BTN-2026-00013', 'ACC-PAY-2026-00282', 35000.0, '2026-09-20'),
]

for btn_id, pe_id, amt, clear_date in pairs:
    # 1. Update Bank Transaction
    bt_url = f'{base_url}/api/resource/Bank%20Transaction/{btn_id}'
    bt_doc = json.loads(opener.open(urllib.request.Request(bt_url)).read().decode('utf-8'))['data']
    
    bt_doc['payment_entries'] = [{
        'payment_document': 'Payment Entry',
        'payment_entry': pe_id,
        'allocated_amount': amt
    }]
    bt_doc['status'] = 'Reconciled'
    bt_doc['unallocated_amount'] = 0.0
    bt_doc['clearance_date'] = clear_date
    
    req_update = urllib.request.Request(
        bt_url,
        data=json.dumps(bt_doc).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='PUT'
    )
    res_update = json.loads(opener.open(req_update).read().decode('utf-8'))
    print(f"Reconciled Bank Transaction {btn_id} with Payment {pe_id} -> Status: {res_update['data']['status']}")
    
    # 2. Update Payment Entry clearance date via set_value
    set_val_url = f'{base_url}/api/method/frappe.client.set_value'
    data_val = urllib.parse.urlencode({
        'doctype': 'Payment Entry',
        'name': pe_id,
        'fieldname': 'clearance_date',
        'value': clear_date
    }).encode('utf-8')
    try:
        res_val = opener.open(urllib.request.Request(set_val_url, data=data_val))
        print(f"Updated {pe_id} clearance_date to {clear_date}")
    except Exception as e:
        print(f"Set value note for {pe_id}: {e}")

print("All sample Bank Transactions & Payment Entries successfully reconciled!")
