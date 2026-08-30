import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
url = "/files/ultra_mrf_logo.png"
# Brand doctype (desk top-left logo)
for brand in frappe.get_all("Brand", pluck="name"):
    b = frappe.get_doc("Brand", brand)
    b.image = url
    b.save(ignore_permissions=True)
    print("Brand updated:", brand)
# also ensure the POS page header/navbar picks up app_logo (it uses Website Settings app_logo)
ws = frappe.get_single("Website Settings")
print("final app_logo:", ws.app_logo, "favicon:", ws.favicon)
frappe.db.commit()
