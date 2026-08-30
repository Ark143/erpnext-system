import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
# fix the existing record to point to the real file
frappe.db.set_value("File", "36a3b62790", {
    "file_name": "ultra_mrf_logo.png",
    "file_url": "/files/ultra_mrf_logo.png",
    "is_private": 0,
})
frappe.db.commit()
# verify
r = frappe.db.get_value("File", "36a3b62790", ["file_name", "file_url", "is_private"], as_dict=True)
print("fixed record:", r)
# now test via get_file path logic: does frappe resolve it?
import os
phys = "/workspace/frappe-bench/sites/site1.local/public/files/ultra_mrf_logo.png"
print("physical exists:", os.path.exists(phys), "size:", os.path.getsize(phys))
