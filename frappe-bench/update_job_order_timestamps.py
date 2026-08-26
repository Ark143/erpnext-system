"""
Script to synchronize DocTypes schema (Vehicle Job Order, Job Order Service Item, Job Order Part Item)
with PostgreSQL database on site1.local and reload them into Frappe cache.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))

import frappe
from frappe.modules.import_file import import_file_by_path
from frappe.model.sync import sync_for

frappe.init("site1.local")
frappe.connect()

print("=== Synchronizing Vehicle Management DocTypes ===")

module_path = frappe.get_app_path("vehicle_management", "vehicle_management", "doctype")

doctypes = [
    "job_order_service_item",
    "job_order_part_item",
    "vehicle_job_order"
]

for dt in doctypes:
    json_path = os.path.join(module_path, dt, f"{dt}.json")
    print(f"Importing {dt} from {json_path}...")
    import_file_by_path(json_path, force=True, ignore_version=True)
    frappe.reload_doctype(frappe.unscrub(dt), force=True)
    print(f"  [OK] Reloaded DocType: {frappe.unscrub(dt)}")

frappe.db.commit()
frappe.clear_cache()
print("\nAll DocTypes successfully reloaded and schema synced!")
