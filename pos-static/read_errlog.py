import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# Read the most recent Error Log for Sales Order Trends
logs = frappe.get_all("Error Log", fields=["name","creation","error"], order_by="creation desc", limit=3)
for l in logs:
    if "trend" in l.error.lower() or "Sales Order" in l.error or "tabSales" in l.error:
        print("=== Error Log", l.name, l.creation, "===")
        print(l.error[:800])
        break
else:
    print("no trend error log found; showing latest 3:")
    for l in logs:
        print(l.name, l.creation, "->", l.error[:120])
