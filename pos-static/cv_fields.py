import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
meta = frappe.get_meta("Customer Vehicle")
fields = [f.fieldname for f in meta.fields if f.fieldtype in ("Data","Link","Select","Date","Int","Float","Small Text","Text")]
print("Customer Vehicle fields:", fields)
# sample row
row = frappe.get_all("Customer Vehicle", fields=["name"]+fields, limit=1)
print("sample:", row)
