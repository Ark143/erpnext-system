import requests
import json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

# Query PLE to calculate true outstanding
ples = s.get('http://38.247.138.224:10017/api/resource/Payment Ledger Entry', params={
    'filters': json.dumps([['against_voucher_no', '=', 'ACC-SINV-2026-00166'], ['delinked', '=', 0]]),
    'fields': json.dumps(['amount', 'amount_in_account_currency'])
}, timeout=30).json().get('data', [])

true_outstanding = sum(float(p['amount']) for p in ples)
print(f"PLE entries count: {len(ples)}, True outstanding amount: {true_outstanding}")

# Also check Job Order JO-2026-00481
jo = s.get('http://38.247.138.224:10017/api/resource/Vehicle Job Order/JO-2026-00481', timeout=30).json().get('data', {})
print(f"Job Order JO-2026-00481: status: {jo.get('status')}, grand_total: {jo.get('grand_total')}, paid: {jo.get('paid_amount')}, sales_invoice: {jo.get('sales_invoice')}")
