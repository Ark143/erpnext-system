import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# 1) Is there a default company?
print("global default company:", frappe.defaults.get_global_default("company"))
print("user default company (Administrator):", frappe.defaults.get_user_default("company", "Administrator"))
print("System Settings country/default company:")
ss=frappe.get_single("System Settings")
print("  country:", ss.country)
# 2) Companies that exist
comps=frappe.get_all("Company", fields=["name"])
print("Companies:", comps)
# 3) The chart widget on the workspace that calls sales_order_trends
print("\n=== Dashboard Chart using sales_order_trends ===")
for dc in frappe.get_all("Dashboard Chart", fields=["name","chart_type","report_name","filters_json","is_default"]):
    if dc.report_name and "trend" in dc.report_name.lower():
        print("  ", dc)
# 4) The workspace chart (chart_widget) referenced - find charts on Vehicle Management workspace
ws=frappe.get_doc("Workspace","Vehicle Management")
import re
charts=set(re.findall(r'"chart[^"]*":\s*"([^"]+)"', ws.content or ""))
links=set(re.findall(r'"link_type":\s*"Dashboard Chart"[^}]*?"[a-z_]+":\s*"([^"]+)"', ws.content or ""))
print("VM workspace chart refs:", charts or links)
