#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")

# Dump the rail nav (build) section + switchView + renderHistory + renderProfile
def dump(start, end, label):
    print(f"\n{'='*20} {label} (chars {start}-{end}) {'='*20}")
    print(html[start:end])

# rail nav structure (around 339800-340400)
dump(339700, 340600, "RAIL NAV / build layout")

# switchView
dump(343300, 343600, "switchView")

# renderHistory (before renderProfile)
dump(345600, 345820, "renderHistory + renderProfile start")
