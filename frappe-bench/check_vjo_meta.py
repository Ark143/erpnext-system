import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

df = frappe.get_meta("Vehicle Job Order").get_field("customer")
print("VJO customer field:", df.fieldtype, df.options)

df_veh = frappe.get_meta("Vehicle Job Order").get_field("vehicle")
print("VJO vehicle field:", df_veh.fieldtype, df_veh.options)
