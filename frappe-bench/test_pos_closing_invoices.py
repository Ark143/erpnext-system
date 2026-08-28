import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import get_invoices

pos_profiles = [r['name'] for r in frappe.db.sql('SELECT name FROM "tabPOS Profile"', as_dict=True)]
print("POS Profiles:", pos_profiles)

if pos_profiles:
    pp = pos_profiles[0]
    res = get_invoices(
        start="2026-08-01 00:00:00",
        end="2026-08-31 23:59:59",
        pos_profile=pp,
        user="Administrator"
    )
    print("get_invoices SUCCESS:", res)
