#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
old = ".vpos-id-logo{width:26px;height:26px;border-radius:7px;background:var(--mint);color:#04201a;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:15px;display:flex;align-items:center;justify-content:center}"
new = ".vpos-id-logo{width:30px;height:30px;border-radius:7px;background:#fff;display:flex;align-items:center;justify-content:center;overflow:hidden}"
n = html.count(old)
print("found:", n)
if n:
    html = html.replace(old, new)
    frappe.db.set_value("Web Page", "vehicle-pos-terminal", "main_section_html", html)
    frappe.db.commit()
    print("patched id-logo css")
else:
    print("NOT FOUND")
