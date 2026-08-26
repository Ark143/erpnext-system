import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

views = ['meta', 'exec_summary', 'sales', 'procurement', 'finance', 'budget', 'approvals', 'operations', 'alerts']
for v in views:
    frappe.response = frappe._dict()
    frappe.form_dict = frappe._dict({'view': v, 'company': 'Ultra MRF Dau Main', 'fy': '2026', 'months': 12})
    doc = frappe.get_doc("Server Script", "Executive Dashboard API")
    doc.execute_method()
    msg = frappe.response.get('message')
    print(f"View [{v:15s}]: Success ({type(msg)}) - Keys/Items: {len(msg) if msg else 0}")
