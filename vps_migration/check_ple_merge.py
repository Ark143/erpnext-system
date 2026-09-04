import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Check PLE for both
ple_res = s.get(f'{URL}/api/resource/Payment%20Ledger%20Entry', params={
    'filters': json.dumps([['voucher_no', 'in', ['ACC-SINV-2026-00163', 'ACC-PSINV-2026-00056']]]),
    'fields': json.dumps(['name', 'voucher_type', 'voucher_no', 'against_voucher_type', 'against_voucher_no', 'account', 'party', 'amount', 'delinked'])
})
print("=== PLE ENTRIES ===")
for p in ple_res.json().get('data', []):
    print(p)
