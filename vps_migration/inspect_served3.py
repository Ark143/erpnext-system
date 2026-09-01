#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")

# 1. download SVG V text + rect (the exact escaped string in JS)
idx = html.find('font-size="14" font-weight="700" fill="#04201a">V</text>')
print("SVG V text at", idx)
if idx >= 0:
    print("CONTEXT:", repr(html[idx-220:idx+40]))

# 2. prof-logo CSS (full minified rule)
i2 = html.find(".vpos-prof-logo{")
print("\nprof-logo css at", i2)
print(repr(html[i2:i2+200]))

# 3. id-logo CSS
i3 = html.find(".vpos-id-logo{")
print("\nid-logo css at", i3)
print(repr(html[i3:i3+200]))

# 4. prof-card h3 css (to anchor img rule insertion)
i4 = html.find(".vpos-prof-card h3{")
print("\nprof-card h3 at", i4)
print(repr(html[i4:i4+120]))

# 5. @media print (for responsive anchor)
i5 = html.find("@media print{")
print("\n@media print at", i5)
print(repr(html[i5:i5+120]))
