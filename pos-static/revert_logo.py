import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
ws = frappe.get_single("Website Settings")
ws.app_logo = "/files/ultra_mrf_logo.png"
ws.save(ignore_permissions=True)
frappe.db.commit()
ws2 = frappe.get_single("Website Settings")
print("app_logo reverted to:", ws2.app_logo)
# cleanup broken File record we created earlier (wrong url)
bad = frappe.db.get_value("File", {"file_url": "/files/ultra_mrf_logo4416e2.png"}, "name")
if bad:
    frappe.delete_doc("File", bad, ignore_permissions=True, force=True)
    print("deleted wrong File record:", bad)
frappe.db.commit()
