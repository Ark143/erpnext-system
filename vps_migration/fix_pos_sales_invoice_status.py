import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# 1. Check all POS Sales Invoices that have outstanding > 0 but are POS / merged
query_code = """
pos_sinvs = frappe.db.sql('''
    SELECT si.name, si.grand_total, si.paid_amount, si.outstanding_amount, si.status, si.is_pos
    FROM `tabSales Invoice` si
    WHERE si.docstatus = 1 
      AND (si.is_pos = 1 OR EXISTS (SELECT 1 FROM `tabPOS Invoice Merge Log` ml WHERE ml.consolidated_invoice = si.name))
''', as_dict=1)

updated = []
for si in pos_sinvs:
    # Check payments or PLE
    payments_sum = frappe.db.sql('''SELECT SUM(amount) FROM `tabSales Invoice Payment` WHERE parent = %s''', si.name)[0][0] or 0.0
    if si.is_pos or payments_sum >= (si.grand_total - 0.01):
        frappe.db.set_value("Sales Invoice", si.name, {
            "outstanding_amount": 0.0,
            "paid_amount": si.grand_total,
            "status": "Paid"
        }, update_modified=False)
        updated.append(si.name)

frappe.db.commit()
frappe.response['message'] = {'updated_count': len(updated), 'updated_invoices': updated}
"""

script_payload = {
    "name": "Fix POS Sales Invoice Status",
    "script_type": "API",
    "api_method": "fix_pos_sinv_status",
    "disabled": 0,
    "script": query_code
}

check_ss = s.get(f'{URL}/api/resource/Server%20Script/Fix%20POS%20Sales%20Invoice%20Status')
if check_ss.status_code == 200:
    res = s.put(f'{URL}/api/resource/Server%20Script/Fix%20POS%20Sales%20Invoice%20Status', json=script_payload)
else:
    res = s.post(f'{URL}/api/resource/Server%20Script', json=script_payload)
print("Server Script status:", res.status_code)

# Run it
exec_res = s.get(f'{URL}/api/method/fix_pos_sinv_status')
print("Execution result:", exec_res.json())

# Check ACC-SINV-2026-00163 now
check_res = s.get(f'{URL}/api/resource/Sales%20Invoice/ACC-SINV-2026-00163')
si = check_res.json().get('data', {})
print("ACC-SINV-2026-00163 Status:", si.get('status'), "| Outstanding:", si.get('outstanding_amount'), "| Paid:", si.get('paid_amount'))
