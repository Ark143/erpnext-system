#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
i = html.find("renderProfile")
print("renderProfile first at", i)
# the function definition (find the one followed by (main) or ())
for marker in ["renderProfile(main)", "renderProfile()", "renderProfile("]:
    j = html.find(marker)
    print(f"  {marker!r} at {j}")
# print from the definition
j = html.find("renderProfile(main)")
if j == -1:
    j = html.find("renderProfile()")
if j == -1:
    j = html.find("renderProfile(")
print("using", j)
print(html[j:j+2600])
