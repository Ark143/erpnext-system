import requests
import json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Get Sales Invoice details
r = s.get(f'{URL}/api/resource/Sales%20Invoice/ACC-SINV-2026-00163')
si = r.json().get('data', {})

print("=== SALES INVOICE ACC-SINV-2026-00163 ===")
print("Status:", si.get('status'))
print("Is POS:", si.get('is_pos'))
print("Grand Total:", si.get('grand_total'))
print("Paid Amount:", si.get('paid_amount'))
print("Outstanding Amount:", si.get('outstanding_amount'))
print("Payments table:", si.get('payments'))

# Get GL Entries for this Sales Invoice
gl_res = s.get(f'{URL}/api/resource/GL%20Entry', params={
    'filters': json.dumps([['voucher_no', '=', 'ACC-SINV-2026-00163']]),
    'fields': json.dumps(['name', 'account', 'debit', 'credit', 'voucher_type', 'voucher_no', 'against'])
})
print("\n=== GL ENTRIES ===")
for gl in gl_res.json().get('data', []):
    print(f"  Account: {gl.get('account')} | Dr: {gl.get('debit')} | Cr: {gl.get('credit')}")

# Get POS Merge Log
merge_res = s.get(f'{URL}/api/resource/POS%20Invoice%20Merge%20Log', params={
    'filters': json.dumps([['consolidated_invoice', '=', 'ACC-SINV-2026-00163']]),
    'fields': json.dumps(['name', 'pos_closing_entry', 'customer'])
})
print("\n=== POS INVOICE MERGE LOG ===")
merge_logs = merge_res.json().get('data', [])
print(merge_logs)

if merge_logs:
    log_name = merge_logs[0].get('name')
    detail_res = s.get(f'{URL}/api/resource/POS%20Invoice%20Merge%20Log/{log_name}')
    detail = detail_res.json().get('data', {})
    print("POS Invoices merged:", detail.get('pos_invoices'))
