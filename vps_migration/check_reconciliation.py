import requests
import json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

# Check all payment entries
pes = s.get('http://38.247.138.224:10017/api/resource/Payment Entry', params={
    'fields': json.dumps(['name', 'party', 'paid_amount', 'docstatus', 'creation']),
    'order_by': 'creation desc',
    'limit': 5
}, timeout=30).json().get('data', [])
print('Recent Payment Entries:', pes)

# Check Sales Invoice status
si = s.get('http://38.247.138.224:10017/api/resource/Sales Invoice/ACC-SINV-2026-00166', timeout=30).json().get('data', {})
print('Sales Invoice status:', si.get('status'), 'outstanding:', si.get('outstanding_amount'), 'grand_total:', si.get('grand_total'))

# Check Payment Entry References pointing to this invoice
refs = s.get('http://38.247.138.224:10017/api/resource/Payment Entry Reference', params={
    'filters': json.dumps([['reference_name', '=', 'ACC-SINV-2026-00166']]),
    'fields': json.dumps(['name', 'parent', 'reference_doctype', 'reference_name', 'total_amount', 'outstanding_amount', 'allocated_amount', 'docstatus'])
}, timeout=30).json().get('data', [])
print('Payment Entry References:', refs)
