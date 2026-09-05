import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Create a Server Script to test if standard POS invoice creation works once opening entry is valid for today
test_script = """
# 1. Close all outdated open entries
outdated = frappe.db.sql('''
    SELECT name, pos_profile, period_start_date, posting_date, user
    FROM `tabPOS Opening Entry`
    WHERE status = 'Open' AND docstatus = 1
''', as_dict=1)

today_str = frappe.utils.today()
closed_count = 0
for oe in outdated:
    start_date = frappe.utils.get_date_str(oe.period_start_date or oe.posting_date)
    if start_date != today_str:
        frappe.db.set_value('POS Opening Entry', oe.name, 'status', 'Closed', update_modified=False)
        closed_count += 1

frappe.db.commit()

# 2. Check if we can create a standard POS Opening Entry for ULTRA MRF today
company = 'ULTRA MRF'
profile_name = 'POS - ULTRA MRF - Administrator'
if not frappe.db.exists('POS Profile', profile_name):
    profile_name = frappe.db.get_value('POS Profile', {'company': company, 'disabled': 0}, 'name')

# Check open entry for today
open_entry = frappe.db.get_value('POS Opening Entry', {'pos_profile': profile_name, 'status': 'Open', 'docstatus': 1}, 'name')
if not open_entry:
    oe = frappe.get_doc({
        'doctype': 'POS Opening Entry',
        'company': company,
        'pos_profile': profile_name,
        'user': 'Administrator',
        'posting_date': frappe.utils.nowdate(),
        'period_start_date': frappe.utils.now_datetime(),
        'balance_details': [{'mode_of_payment': 'Cash', 'opening_amount': 500}]
    })
    oe.insert(ignore_permissions=True)
    oe.submit()
    frappe.db.commit()
    open_entry = oe.name

# 3. Try creating a POS Invoice
cust = frappe.db.get_value('Customer', {}, 'name')
item = frappe.db.get_value('Item', {'is_sales_item': 1, 'disabled': 0}, 'name')

pos_inv = frappe.get_doc({
    'doctype': 'POS Invoice',
    'naming_series': 'ACC-PSINV-.YYYY.-',
    'company': company,
    'customer': cust,
    'pos_profile': profile_name,
    'posting_date': frappe.utils.nowdate(),
    'items': [{
        'item_code': item,
        'qty': 1,
        'rate': 500,
        'uom': 'Nos'
    }],
    'payments': [{
        'mode_of_payment': 'Cash',
        'amount': 500
    }]
})
pos_inv.insert(ignore_permissions=True)
pos_inv.submit()
frappe.db.commit()

frappe.response['message'] = {
    'status': 'success',
    'closed_stale_entries': closed_count,
    'open_entry': open_entry,
    'pos_invoice': pos_inv.name,
    'grand_total': pos_inv.grand_total,
    'docstatus': pos_inv.docstatus
}
"""

script_payload = {
    "name": "Test POS Shift and Invoice",
    "script_type": "API",
    "api_method": "test_pos_shift_invoice",
    "disabled": 0,
    "script": test_script
}

check_ss = s.get(f'{URL}/api/resource/Server%20Script/Test%20POS%20Shift%20and%20Invoice')
if check_ss.status_code == 200:
    s.put(f'{URL}/api/resource/Server%20Script/Test%20POS%20Shift%20and%20Invoice', json=script_payload)
else:
    s.post(f'{URL}/api/resource/Server%20Script', json=script_payload)

exec_res = s.get(f'{URL}/api/method/test_pos_shift_invoice')
print("Execution result:", json.dumps(exec_res.json(), indent=2))
