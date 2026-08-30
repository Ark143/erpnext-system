import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
print("=== Workspaces ===")
for w in frappe.get_all("Workspace", fields=["name","module","icon","label","route"]):
    print(f"  {w.name:28} | module={str(w.module):20} | icon={w.icon} | label={w.label} | route={w.route}")
print("\n=== Does 'Vehicle Management' workspace exist? ===")
print("  exists:", frappe.db.exists("Workspace","Vehicle Management"))
# The error triggers when desk sidebar has an app/icon with missing icon.
# Check Desk Settings sidebar_items or the app's workspace icon for vehicle_management
print("\n=== apps.txt / installed apps ===")
import os
apps=open("/workspace/frappe-bench/sites/apps.txt").read().splitlines()
print(" ", apps)
