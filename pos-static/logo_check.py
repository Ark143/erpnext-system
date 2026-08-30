import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
print("File doctype exists ultra_mrf_logo.png:", frappe.db.exists("File", "ultra_mrf_logo.png"))
r = frappe.db.get_value("File", "ultra_mrf_logo.png", ["file_url", "file_name", "is_private"], as_dict=True)
print("File record:", r)
