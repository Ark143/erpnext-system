import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
url = "/files/ultra_mrf_logo.png"
# Website Settings
ws = frappe.get_single("Website Settings")
ws.app_logo = url
ws.favicon = url
ws.save(ignore_permissions=True)
# System Settings brand
ss = frappe.get_single("System Settings")
ss.app_logo = url
ss.favicon = url
ss.save(ignore_permissions=True)
# Brand doctype
if frappe.db.exists("Brand", "ERPNext"):
    b = frappe.get_doc("Brand", "ERPNext")
    b.brand_name = "ULTRA MRF"
    b.image = url
    b.save(ignore_permissions=True)
frappe.db.commit()
print("app_logo:", ws.app_logo, "| favicon:", ws.favicon)
print("system app_logo:", ss.app_logo)
