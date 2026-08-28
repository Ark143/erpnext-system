import sys, os
sys.path.insert(0, r"C:\Users\josem\erpnext-system\frappe-bench\apps\frappe")
sys.path.insert(0, r"C:\Users\josem\erpnext-system\frappe-bench\apps\erpnext")
sys.path.insert(0, r"C:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management")
import frappe

SITES = r"C:\Users\josem\erpnext-system\frappe-bench\sites"
for site in ["erp.localhost", "site1.local"]:
    try:
        frappe.init(site=site, sites_path=SITES)
        frappe.connect()
        apps = frappe.get_installed_apps()
        has_vm = "vehicle_management" in apps
        counts = {}
        for dt in ["Company","Cost Center","Warehouse","Sales Person","Customer Vehicle","Bin Location",
                   "Vehicle Estimate","Vehicle Job Order","Vehicle Inspection","Purchase Order",
                   "Purchase Receipt","Purchase Invoice","Sales Invoice","Payment Entry","Stock Entry"]:
            try:
                counts[dt] = frappe.db.count(dt)
            except Exception as e:
                counts[dt] = f"ERR:{e}"
        print(f"\n### SITE {site} | vm_installed={has_vm}")
        print("  apps:", apps)
        for k,v in counts.items():
            print(f"  {k}: {v}")
        frappe.destroy()
    except Exception as e:
        print(f"\n### SITE {site} INIT FAILED: {e}")
