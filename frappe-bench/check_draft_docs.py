import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

doctypes = [
    ("Vehicle Job Order", "grand_total" if frappe.db.has_column("Vehicle Job Order", "grand_total") else "0", "creation"),
    ("Vehicle Inspection", "0", "creation"),
    ("Sales Order", "grand_total", "transaction_date"),
    ("Sales Invoice", "grand_total", "posting_date"),
    ("Purchase Order", "grand_total", "transaction_date"),
    ("Purchase Invoice", "grand_total", "posting_date"),
    ("Payment Entry", "paid_amount", "posting_date"),
    ("Journal Entry", "total_debit", "posting_date"),
    ("Material Request", "0", "transaction_date"),
]

for dt, col, date_col in doctypes:
    if frappe.db.table_exists(dt):
        has_company = frappe.db.has_column(dt, "company")
        if has_company:
            sql = f'SELECT COUNT(name) as cnt, COALESCE(SUM({col}), 0) as tot FROM "tab{dt}" WHERE docstatus = 0 AND company = %s'
            res = frappe.db.sql(sql, ("Ultra MRF Dau Main",), as_dict=True)[0]
        else:
            sql = f'SELECT COUNT(name) as cnt, COALESCE(SUM({col}), 0) as tot FROM "tab{dt}" WHERE docstatus = 0'
            res = frappe.db.sql(sql, as_dict=True)[0]
        print(f"DocType: {dt:25s} -> Drafts: {res['cnt']}, Total Value: {res['tot']}")
    else:
        print(f"DocType: {dt:25s} -> NOT FOUND")
