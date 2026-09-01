#!/usr/bin/env python3
import frappe, re
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
# find downloadCard function and its SVG logo "V"
idx = html.find("downloadCard")
print("downloadCard at", idx)
if idx >= 0:
    print(repr(html[idx:idx+2000]))
print("\n\n=== search for '>V</text>' or 'V</text>' ===")
for m in re.finditer(r'V</text>', html):
    print("at", m.start(), repr(html[m.start()-120:m.start()+60]))
print("\n=== search '>V<' in svg/rect context ===")
for m in re.finditer(r'>V</(text|div)>', html):
    print("at", m.start(), repr(html[m.start()-160:m.start()+60]))
