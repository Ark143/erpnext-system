import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

doctypes = ["Sales Order", "Delivery Note", "Sales Invoice", "Purchase Order", "Purchase Receipt", "Purchase Invoice", "Stock Entry", "Payment Entry"]
print("=== Current System Document Totals ===")
for dt in doctypes:
    total = frappe.db.sql(f'SELECT COUNT(*) FROM "tab{dt}"')[0][0]
    print(f"  {dt:20s}: {total}")
