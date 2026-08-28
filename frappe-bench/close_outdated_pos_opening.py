import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
os.chdir('sites')
import frappe
from frappe.utils import nowdate, now_datetime
from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import make_closing_entry_from_opening

frappe.init(site='erp.localhost')
frappe.connect()

opening_name = "POS-OPE-2026-00001"
if frappe.db.exists("POS Opening Entry", opening_name):
    op = frappe.get_doc("POS Opening Entry", opening_name)
    if op.status == "Open":
        # Create Closing Entry
        closing = make_closing_entry_from_opening(op)
        closing.insert()
        closing.submit()
        print(f"Closed {opening_name} with POS Closing Entry: {closing.name}")

# Also let's ensure today's POS Opening Entry can be opened
openings = frappe.db.sql('SELECT name, status, posting_date FROM "tabPOS Opening Entry"', as_dict=True)
print("Updated POS Opening status:", openings)
