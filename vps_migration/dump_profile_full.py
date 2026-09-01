#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")

# Full renderProfile body (from renderProfile to downloadCard)
i = html.find("renderProfile(){")
j = html.find("downloadCard(){")
print(f"renderProfile {i} -> downloadCard {j}")
print(html[i:j])
