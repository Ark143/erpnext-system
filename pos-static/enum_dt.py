import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# Enumerate DocTypes in the vehicle_management module + standard master DocTypes, with counts
import json
docs = frappe.get_all("DocType", filters={"module": "Vehicle Management"}, fields=["name"])
print("=== Vehicle Management DocTypes ===")
for d in docs:
    try:
        n = frappe.db.count(d["name"])
    except Exception as e:
        n = f"?{e}"
    print(f"{d['name']}: {n}")
print("=== Standard master data counts ===")
for dt in ["Customer","Supplier","Item","Item Group","Customer Group","Supplier Group","Price List","Vehicle Make","Vehicle Model","Customer Vehicle","Bin","Brand","Warehouse","Account","Cost Center","POS Profile","Mode of Payment"]:
    try:
        n = frappe.db.count(dt)
    except Exception as e:
        n = f"?{e}"
    print(f"{dt}: {n}")
