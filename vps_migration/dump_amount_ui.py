#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
for m in ["openCashier(){", "closeCashier(){", "loadShift(){"]:
    i = html.find(m)
    print(f"=== {m} at {i} ===")
    if i != -1:
        print(repr(html[i:i+700]))
    print()
