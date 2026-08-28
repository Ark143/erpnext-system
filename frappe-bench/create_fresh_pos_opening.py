import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
os.chdir('sites')
import frappe
from frappe.utils import nowdate, now_datetime

frappe.init(site='erp.localhost')
frappe.connect()

user = "Administrator"
pos_profile = "JM"
company = "Ultra MRF Dau Annex"

active = frappe.db.get_value("POS Opening Entry", {"user": user, "pos_profile": pos_profile, "status": "Open"}, "name")
if not active:
    ope = frappe.new_doc("POS Opening Entry")
    ope.user = user
    ope.pos_profile = pos_profile
    ope.company = company
    ope.period_start_date = now_datetime()
    ope.posting_date = nowdate()
    ope.append("balance_details", {
        "mode_of_payment": "Cash",
        "opening_amount": 1000.0
    })
    ope.insert()
    ope.submit()
    print(f"SUCCESS: Created active POS Opening Entry: {ope.name} for {company} on {nowdate()}")
else:
    print(f"Active POS Opening Entry already exists: {active}")
