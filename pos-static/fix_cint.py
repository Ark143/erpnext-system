import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
d = frappe.get_doc("Server Script", "Executive Dashboard API")
s = d.script
n = s.count("cint(")
s = s.replace("cint(", "int(")
d.script = s
d.save()
frappe.db.commit()
print(f"Executive Dashboard API: replaced cint( -> int( x{n}")
