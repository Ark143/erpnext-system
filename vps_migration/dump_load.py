#!/usr/bin/env python3
import frappe, re
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")

# api helper + load function
for kw in ["async load()", "load(){", "api(", "const api=", "function api(", "vm_pos_history", "vm_pos_meta", "vm_pos_cashier"]:
    for m in re.finditer(re.escape(kw), html):
        print(f"=== {kw!r} at {m.start()} ===")
        print(repr(html[m.start()-40:m.start()+300]))
        print()
        break  # first occurrence only
