import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

doctypes = [r['name'] for r in frappe.db.sql('SELECT name FROM "tabDocType" WHERE name LIKE %s', ('%Vehicle%',), as_dict=True)]
print("Vehicle Doctypes:", doctypes)
