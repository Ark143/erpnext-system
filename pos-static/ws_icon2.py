import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# List all workspaces with their module + icon
print("=== All Workspaces (name | module | icon) ===")
for w in frappe.get_all("Workspace", fields=["name","module","icon","label"]):
    print(f"  {w.name:30} module={w.module} icon={w.icon} label={w.label}")
# Find vehicle_management app workspace specifically
print("\n=== vehicle_management workspaces ===")
for w in frappe.get_all("Workspace", fields=["name","module","icon","label","content"]):
    if "vehicle" in (w.module or "").lower() or "vehicle" in (w.name or "").lower() or "vehicle" in (w.label or "").lower():
        print(f"  FOUND: {w.name} module={w.module} icon={w.icon}")
# Also check the app's module def icon via db
print("\n=== Module Def Vehicle Management raw ===")
row=frappe.db.get_value("Module Def","Vehicle Management",["name","app_name","icon","color"],as_dict=True)
print(" ", row)
