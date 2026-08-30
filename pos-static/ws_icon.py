import frappe, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
print("=== Workspaces ===")
for w in frappe.get_all("Workspace", pluck="name"):
    print(" ", w)
print("=== Module Def: Vehicle Management ===")
if frappe.db.exists("Module Def","Vehicle Management"):
    m=frappe.get_doc("Module Def","Vehicle Management")
    print(" icon:", m.icon, "| app_name:", m.app_name)
else:
    print(" Module Def 'Vehicle Management' does NOT exist")
# find the workspace that references vehicle management
print("=== Workspace docs with 'vehicle' in content ===")
for w in frappe.get_all("Workspace", pluck="name"):
    doc=frappe.get_doc("Workspace", w)
    txt=(doc.content or "")+(doc.module or "")
    if "vehicle" in txt.lower() or "vehicle_management" in txt.lower():
        print(f"  {w}: module={doc.module} icon={doc.icon}")
# Icons: check desk sidebar config
print("=== Desk Settings / sidebar ===")
ds=frappe.get_single("System Settings")
print(" app_name:", ds.app_name)
