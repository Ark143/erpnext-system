#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
d = frappe.get_doc("Web Page", "vehicle-pos-terminal")
html = d.main_section_html or ""
print("main_section_html len:", len(html))
with open("/tmp/pos_terminal_spa.html", "w", encoding="utf-8") as f:
    f.write(html)
print("written /tmp/pos_terminal_spa.html")
print("has vpos-root:", "<div class=\"vpos-root\"" in html or 'id="vpos-root"' in html)
print("has POS.init:", "POS.init" in html)
print("has vm_pos_vehicle_customer:", "vm_pos_vehicle_customer" in html)
