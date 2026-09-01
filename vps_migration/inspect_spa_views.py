#!/usr/bin/env python3
import frappe, re
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
# find view definitions / rail icons / data-view
print("=== data-view occurrences ===")
for m in re.finditer(r'data-view[=:]["\']?(\w+)', html):
    print("  view:", m.group(1), "at", m.start())
print("\n=== renderProfile / renderHistory / build() / switchView ===")
for fn in ["renderProfile", "renderHistory", "renderHistory", "history", "switchView", "showView", "openView", "renderView", "build(){", "load()", "renderHome", "renderCart", "renderTicket"]:
    idx = html.find(fn)
    print(f"  {fn!r} at {idx}")
