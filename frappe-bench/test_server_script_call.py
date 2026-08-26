import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

frappe.form_dict = frappe._dict({'view': 'meta', 'company': 'Ultra MRF Dau Main'})
doc = frappe.get_doc("Server Script", "Executive Dashboard API")
res = doc.execute_method()
print("Server Script execute_method response:", frappe.response.get('message'))

frappe.form_dict = frappe._dict({'view': 'exec_summary', 'company': 'Ultra MRF Dau Main', 'fy': '2026'})
res2 = doc.execute_method()
print("Server Script exec_summary Revenue:", frappe.response.get('message', {}).get('revenue'))
