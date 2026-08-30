import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# Modules
mods = frappe.get_all("Module Def", fields=["name"], order_by="name")
print("MODULES:", len(mods))
for m in mods: print("  ", m["name"])
# Vehicle Management doctypes
vms = frappe.get_all("DocType", filters={"module":"Vehicle Management"}, fields=["name"], order_by="name")
print("\nVEHICLE MGMT DOCTYPES:", len(vms))
for d in vms: print("  ", d["name"])
