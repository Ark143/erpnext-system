#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
i = html.find("openScanner(){")
print("openScanner(){ at", i)
if i == -1:
    # try "openScanner() {" with space
    i = html.find("openScanner() {")
    print("openScanner() { at", i)
print(repr(html[i:i+1200]))
