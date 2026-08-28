import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

doctypes = [
    "Vehicle Job Order", "Vehicle Inspection", "Sales Order", "Sales Invoice",
    "Purchase Order", "Purchase Invoice", "Payment Entry", "Journal Entry", "Material Request"
]

print("=== DocStatus Breakdown across System ===")
for dt in doctypes:
    if frappe.db.table_exists(dt):
        drafts = frappe.db.sql(f'SELECT COUNT(*) FROM "tab{dt}" WHERE docstatus = 0')[0][0]
        submitted = frappe.db.sql(f'SELECT COUNT(*) FROM "tab{dt}" WHERE docstatus = 1')[0][0]
        cancelled = frappe.db.sql(f'SELECT COUNT(*) FROM "tab{dt}" WHERE docstatus = 2')[0][0]
        print(f"  {dt:22s} | Drafts (Pending Approval): {drafts:3d} | Submitted: {submitted:3d} | Cancelled: {cancelled:3d}")
