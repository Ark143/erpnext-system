#!/usr/bin/env python3
import frappe, re
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
# find the "V" in the SVG download section and CSS rules
for marker in ["Mint accent", "vpos-prof-logo", "vpos-id-logo", "mintg", "text-anchor=\"middle\">V</text>", "@media print", "vpos-prof-card h3"]:
    idx = html.find(marker)
    print(f"=== {marker!r} at {idx} ===")
    if idx >= 0:
        print(repr(html[idx-80:idx+200]))
    print()
