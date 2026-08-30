import frappe, inspect
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
import vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice as m
src = inspect.getsource(m)
for line in src.splitlines():
    low = line.lower()
    if any(k in low for k in ["def validate", "customer", "vehicle", "does not match", "owner", "match"]):
        print(line)
