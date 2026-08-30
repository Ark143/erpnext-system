import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# find Dashboard Charts using sales_order_trends (avoid is_default column)
charts = frappe.get_all("Dashboard Chart", pluck="name")
for cname in charts:
    dc = frappe.get_doc("Dashboard Chart", cname)
    if dc.report_name and "trend" in dc.report_name.lower():
        print("CHART:", cname, "| report:", dc.report_name, "| filters_json:", dc.filters_json, "| type:", dc.chart_type)
# Also: which workspace embeds this chart?
print("\n=== workspaces mentioning sales_order_trends / trend charts ===")
for w in frappe.get_all("Workspace", pluck="name"):
    doc = frappe.get_doc("Workspace", w)
    if "trend" in (doc.content or "").lower():
        print("  workspace:", w)
