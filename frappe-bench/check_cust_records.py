import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

custs = frappe.db.sql('SELECT name, customer_name FROM "tabCustomer" LIMIT 10', as_dict=True)
for c in custs:
    print(c)
