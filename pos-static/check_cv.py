import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# Customer Vehicle link field to customer
cv = frappe.get_doc("DocType", "Customer Vehicle")
links = [f.fieldname for f in cv.fields if f.fieldtype in ("Link",) and f.options == "Customer"]
print("Customer Vehicle customer-link fields:", links)
# sample row
row = frappe.get_all("Customer Vehicle", fields=links + ["name"], limit=1)
print("sample:", row)
