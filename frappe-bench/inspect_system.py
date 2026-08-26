import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
frappe.init(site='erp.localhost')
frappe.connect()

print("Companies:")
for c in frappe.db.sql('SELECT name, abbr, default_currency FROM "tabCompany"', as_dict=True):
    print(" ", c)

print("\nFiscal Years:")
for f in frappe.db.sql('SELECT name, year_start_date, year_end_date FROM "tabFiscal Year"', as_dict=True):
    print(" ", f)

print("\nDefault company:", frappe.db.get_single_value("Global Defaults", "default_company"))

print("\nInvoices per company:")
for row in frappe.db.sql('SELECT company, count(name) as cnt, sum(grand_total) as tot FROM "tabSales Invoice" WHERE docstatus=1 GROUP BY company', as_dict=True):
    print(" ", row)

print("\nPurchase Invoices per company:")
for row in frappe.db.sql('SELECT company, count(name) as cnt, sum(grand_total) as tot FROM "tabPurchase Invoice" WHERE docstatus=1 GROUP BY company', as_dict=True):
    print(" ", row)

print("\nGL Entries per company:")
for row in frappe.db.sql('SELECT company, count(name) as cnt FROM "tabGL Entry" WHERE docstatus=1 GROUP BY company', as_dict=True):
    print(" ", row)
