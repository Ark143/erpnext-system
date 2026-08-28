import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')

import frappe
frappe.init('site1.local')
frappe.connect()

comp = 'ULTRA MRF'
cust = frappe.get_all('Customer', limit=1)[0]['name']
items = frappe.get_all('Item', filters={'disabled': 0}, limit=10)

for it in items:
    try:
        si = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'company': comp,
            'customer': cust,
            'items': [{'item_code': it['name'], 'qty': 1, 'rate': 1000}]
        })
        si.insert(ignore_permissions=True)
        print("SUCCESS for item:", it['name'])
        frappe.db.rollback()
    except Exception as e:
        print(f"FAILED for item {it['name']}: {type(e).__name__} - {e}")
        frappe.db.rollback()
