import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# valid Workspace columns (avoid route/icon if missing) - query raw
cols = frappe.db.get_table_columns("Workspace")
print("Workspace columns:", cols)
# pick safe ones
safe=[c for c in ["name","module","label","icon","app","is_default","parent_website_route"] if c in cols]
print("safe:", safe)
rows=frappe.get_all("Workspace", fields=safe)
for r in rows:
    print("  ", r)
print("\nVehicle Management workspace exists:", frappe.db.exists("Workspace","Vehicle Management"))
vm=frappe.db.get_value("Workspace","Vehicle Management", safe, as_dict=True) if frappe.db.exists("Workspace","Vehicle Management") else None
print("VM workspace:", vm)
# Module Def columns
print("\nModule Def columns:", frappe.db.get_table_columns("Module Def"))
