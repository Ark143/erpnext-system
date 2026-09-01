#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")

def dump(start, end, label):
    print(f"\n{'='*20} {label} ({start}-{end}) {'='*20}")
    print(html[start:end])

# find switchView full (search backward for "switchView(" def)
i = html.find("switchView(v)")
print("switchView(v) at", i)
if i == -1:
    i = html.find("switchView")
print("switchView at", i)
dump(i, i+800, "switchView full")

# find renderHistory full body (between renderHistory(){ and next method)
j = html.find("renderHistory(){")
print("\nrenderHistory at", j)
dump(j, j+1600, "renderHistory full")
