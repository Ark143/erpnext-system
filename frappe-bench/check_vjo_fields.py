import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

meta = frappe.get_meta("Vehicle Job Order")
print("VJO required fields:", [df.fieldname for df in meta.fields if df.reqd])

cust_vehicles = [r['name'] for r in frappe.db.sql('SELECT name FROM "tabCustomer Vehicle"', as_dict=True)]
print("Customer Vehicles:", cust_vehicles[:5])
