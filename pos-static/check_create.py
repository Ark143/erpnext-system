import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# Does create_from_pos exist on the doctype?
import os
p = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/doctype/vehicle_pos_invoice/vehicle_pos_invoice.py"
print("file exists:", os.path.exists(p))
if os.path.exists(p):
    src = open(p).read()
    print("has create_from_pos:", "create_from_pos" in src)
    # print its signature + first 40 lines
    import re
    m = re.search(r"def create_from_pos.*?:", src)
    print("sig:", m.group(0) if m else "NOT FOUND")
# companies available
print("companies:", [c["name"] for c in frappe.get_all("Company", filters={"is_group":0}, fields=["name"])][:5])
