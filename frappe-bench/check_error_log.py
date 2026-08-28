import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')

import frappe
frappe.init('site1.local')
frappe.connect()

err = frappe.db.sql('SELECT method, error FROM "tabError Log" ORDER BY creation DESC LIMIT 1', as_dict=True)
if err:
    print("Method:", err[0]['method'])
    print("Error:\n", err[0]['error'])
else:
    print("No error logs found.")
