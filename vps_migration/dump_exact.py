#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")

# full renderHistory (exact)
i = html.find("renderHistory(){")
print("=== renderHistory full ===")
print(repr(html[i:i+700]))

# full renderProfile from (main){ to downloadCard
j = html.find("renderProfile(main){")
k = html.find("downloadCard(){")
print("\n\n=== renderProfile FULL (exact) ===")
print(repr(html[j:k]))

# peso helper
p = html.find("peso(")
print("\n\n=== peso helper ===")
print(repr(html[p-100:p+200]))
