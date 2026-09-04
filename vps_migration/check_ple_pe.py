import requests
import json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

ples = s.get('http://38.247.138.224:10017/api/resource/Payment Ledger Entry', params={
    'filters': json.dumps([['voucher_no', '=', 'ACC-PAY-2026-00222']]),
    'fields': json.dumps(['name', 'voucher_type', 'voucher_no', 'against_voucher_type', 'against_voucher_no', 'account', 'party', 'amount', 'delinked'])
}, timeout=30).json().get('data', [])

print("Payment Ledger Entries for ACC-PAY-2026-00222:", ples)

# Also let's check update_outstanding_amounts on Sales Invoice
# In ERPNext: when Payment Entry is submitted, it calls update_outstanding_amounts()
res = s.get('http://38.247.138.224:10017/api/resource/GL Entry', params={
    'filters': json.dumps([['voucher_no', '=', 'ACC-PAY-2026-00222']]),
    'fields': json.dumps(['name', 'account', 'debit', 'credit', 'against_voucher'])
}, timeout=30).json().get('data', [])
print("GL Entries for ACC-PAY-2026-00222:", res)
