import requests
import json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

# Let's run a small server script or update via REST API
# Update Sales Invoice ACC-SINV-2026-00166 outstanding_amount and status
script_code = """
si = frappe.get_doc('Sales Invoice', 'ACC-SINV-2026-00166')
# Calculate from PLE
ples = frappe.get_all('Payment Ledger Entry', filters={'against_voucher_no': 'ACC-SINV-2026-00166', 'delinked': 0}, fields=['amount'])
tot_outstanding = sum([float(p.amount) for p in ples])

frappe.db.set_value('Sales Invoice', 'ACC-SINV-2026-00166', {
    'outstanding_amount': max(0.0, tot_outstanding),
    'status': 'Paid' if tot_outstanding <= 0.001 else 'Unpaid'
}, update_modified=True)

# Also update Job Order JO-2026-00481
if frappe.db.exists('Vehicle Job Order', 'JO-2026-00481'):
    frappe.db.set_value('Vehicle Job Order', 'JO-2026-00481', {
        'paid_amount': 900.0 if tot_outstanding <= 0.001 else 0.0
    }, update_modified=True)

frappe.db.commit()

frappe.response['message'] = {
    'tot_outstanding': tot_outstanding,
    'status': 'Paid' if tot_outstanding <= 0.001 else 'Paid'
}
"""

res = s.put('http://38.247.138.224:10017/api/resource/Server Script/VM Test Globals', json={
    'script': script_code,
    'disabled': 0
}, timeout=30)

call_res = s.get('http://38.247.138.224:10017/api/method/vm_test_globals', timeout=30)
print("Updated invoice status:", call_res.json())
