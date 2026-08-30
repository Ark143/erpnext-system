import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
v = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html") or ""
for needle in ["ultra_mrf_logo", "navbar-brand", "/files/ultra_mrf_logo.png"]:
    print(needle, "->", v.count(needle))
# show context around the navbar-brand if present
i = v.find("navbar-brand")
if i >= 0:
    print("navbar context:", v[i-40:i+120])
j = v.find("ultra_mrf_logo")
if j >= 0:
    print("logo context:", v[j-60:j+80])
