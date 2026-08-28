import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

openings = frappe.db.sql('SELECT name, period_start_date, posting_date, status, user, pos_profile, company FROM "tabPOS Opening Entry"', as_dict=True)
print("POS Opening Entries in DB:")
for op in openings:
    print(op)
