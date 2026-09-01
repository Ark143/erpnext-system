#!/usr/bin/env python3
import frappe, re
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
# find all vpos-prof-logo and vpos-id-logo usages (both css and html)
for cls in ["vpos-prof-logo", "vpos-id-logo"]:
    print(f"===== {cls} =====")
    for m in re.finditer(re.escape(cls), html):
        s = m.start()
        print(f"  at {s}: ...{html[max(0,s-10):s+80]!r}")
    print()
# find the renderProfile HTML "V" instances
print("===== '>V</div>' =====")
for m in re.finditer(r'>V</div>', html):
    print(f"  at {m.start()}: ...{html[max(0,m.start()-60):m.start()+20]!r}")
