import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_mode_of_payments_info

company = "Ultra MRF Dau Main"
mops = ["Cash", "Credit Card", "Bank Draft", "Cheque", "Wire Transfer"]
existing_mops = [r['name'] for r in frappe.db.sql('SELECT name FROM "tabMode of Payment"', as_dict=True)]
print("Existing Modes of Payment:", existing_mops)

res = get_mode_of_payments_info(tuple(existing_mops), company)
print("get_mode_of_payments_info SUCCESS:", res)

# Test creating / validating a sales invoice
si = frappe.new_doc("Sales Invoice")
si.company = company
si.customer = frappe.db.get_value("Customer", {}, "name") or "Walk-in Customer"
si.is_pos = 1
si.set_missing_values()
print("Sales Invoice POS set_missing_values SUCCESS!")
