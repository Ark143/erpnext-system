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

company = 'Automan Car Care Center'
bank_account_doc = 'Automan Operating Account - BDO Unibank, Inc.'
gl_account = 'BDO - AUTOMAN'

# Get customer & supplier
req_cust = opener.open(urllib.request.Request(f'{base_url}/api/resource/Customer?limit=1'))
cust = json.loads(req_cust.read().decode('utf-8'))['data'][0]['name']

req_supp = opener.open(urllib.request.Request(f'{base_url}/api/resource/Supplier?limit=1'))
supp = json.loads(req_supp.read().decode('utf-8'))['data'][0]['name']

print(f'Customer: {cust}, Supplier: {supp}')

samples = [
    {'type': 'Receive', 'amt': 15000, 'date': '2026-09-02', 'party_type': 'Customer', 'party': cust, 'ref': 'DEP-2026-001', 'account_field': 'paid_to'},
    {'type': 'Pay', 'amt': 4500, 'date': '2026-09-05', 'party_type': 'Supplier', 'party': supp, 'ref': 'CHQ-2026-002', 'account_field': 'paid_from'},
    {'type': 'Receive', 'amt': 22000, 'date': '2026-09-10', 'party_type': 'Customer', 'party': cust, 'ref': 'DEP-2026-003', 'account_field': 'paid_to'},
    {'type': 'Pay', 'amt': 1500, 'date': '2026-09-15', 'party_type': 'Supplier', 'party': supp, 'ref': 'FEE-2026-004', 'account_field': 'paid_from'},
    {'type': 'Receive', 'amt': 35000, 'date': '2026-09-20', 'party_type': 'Customer', 'party': cust, 'ref': 'DEP-2026-005', 'account_field': 'paid_to'}
]

for s in samples:
    check_url = f'{base_url}/api/resource/Payment%20Entry?filters=' + urllib.parse.quote(json.dumps([['reference_no', '=', s['ref']]]))
    res = json.loads(opener.open(urllib.request.Request(check_url)).read().decode('utf-8'))
    if res.get('data'):
        print(f"Payment Entry for {s['ref']} already exists: {res['data'][0]['name']}")
        continue
    
    doc = {
        'doctype': 'Payment Entry',
        'payment_type': s['type'],
        'company': company,
        'posting_date': s['date'],
        'mode_of_payment': 'Bank Draft',
        'party_type': s['party_type'],
        'party': s['party'],
        s['account_field']: gl_account,
        'paid_amount': s['amt'],
        'received_amount': s['amt'],
        'reference_no': s['ref'],
        'reference_date': s['date']
    }
    
    req_create = urllib.request.Request(
        f'{base_url}/api/resource/Payment%20Entry',
        data=json.dumps(doc).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res_create = json.loads(opener.open(req_create).read().decode('utf-8'))
    pe_name = res_create['data']['name']
    
    # Submit Payment Entry
    req_submit = urllib.request.Request(
        f'{base_url}/api/resource/Payment%20Entry/{pe_name}',
        data=json.dumps({'docstatus': 1}).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='PUT'
    )
    res_submit = json.loads(opener.open(req_submit).read().decode('utf-8'))
    print(f"Submitted Payment Entry: {pe_name} for {s['ref']} ({s['amt']} PHP)")

print("All sample Payment Entries successfully prepared!")

# Create corresponding Bank Transactions from Statement
bt_entries = [
    {'date': '2026-09-02', 'deposit': 15000.0, 'withdrawal': 0.0, 'ref': 'DEP-2026-001', 'desc': 'Customer Direct Deposit Ref 001'},
    {'date': '2026-09-05', 'deposit': 0.0, 'withdrawal': 4500.0, 'ref': 'CHQ-2026-002', 'desc': 'Supplier Payment Auto-Debit'},
    {'date': '2026-09-10', 'deposit': 22000.0, 'withdrawal': 0.0, 'ref': 'DEP-2026-003', 'desc': 'Check Clearing Collection'},
    {'date': '2026-09-15', 'deposit': 0.0, 'withdrawal': 1500.0, 'ref': 'FEE-2026-004', 'desc': 'Monthly Bank Maintenance Fee'},
    {'date': '2026-09-20', 'deposit': 35000.0, 'withdrawal': 0.0, 'ref': 'DEP-2026-005', 'desc': 'Corporate Fleet Service Payment'}
]

for e in bt_entries:
    check_url = f"{base_url}/api/resource/Bank%20Transaction?filters=" + urllib.parse.quote(json.dumps([['reference_number', '=', e['ref']]]))
    res = json.loads(opener.open(urllib.request.Request(check_url)).read().decode('utf-8'))
    if res.get('data'):
        print(f"Bank Transaction for {e['ref']} already exists: {res['data'][0]['name']}")
        continue
    
    doc = {
        'doctype': 'Bank Transaction',
        'date': e['date'],
        'bank_account': bank_account_doc,
        'company': company,
        'deposit': e['deposit'],
        'withdrawal': e['withdrawal'],
        'reference_number': e['ref'],
        'description': e['desc'],
        'status': 'Unreconciled',
        'unallocated_amount': e['deposit'] if e['deposit'] > 0 else e['withdrawal'],
        'docstatus': 1
    }
    
    req_create = urllib.request.Request(
        f"{base_url}/api/resource/Bank%20Transaction",
        data=json.dumps(doc).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res_create = json.loads(opener.open(req_create).read().decode('utf-8'))
    print(f"Created Bank Transaction: {res_create['data']['name']} for {e['ref']}")

print("Setup completed successfully!")
