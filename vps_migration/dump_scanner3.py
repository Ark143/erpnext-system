#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
i = html.find("openScanner(){")
j = html.find("build(){", i)
print("from", i, "to build", j)
# print the tail end of openScanner (last 600 chars before build)
print(repr(html[j-600:j]))
