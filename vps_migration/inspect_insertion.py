#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
i = html.find("href='data:image/png;base64,")
# print the region before the data url start
print("=== 200 chars BEFORE data url ===")
print(repr(html[i-200:i]))
print("\n=== first 80 chars of data url ===")
print(repr(html[i:i+80]))
print("\n=== chars around the END of the whole svg string (after data url + preserve...) ===")
# find preserveAspectRatio after the data url
j = html.find("preserveAspectRatio", i)
print(repr(html[j-40:j+80]))
