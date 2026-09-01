import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
logs = frappe.get_all("Error Log", fields=["name","creation","error"], order_by="creation desc", limit=6)
for l in logs:
    print("====", l["creation"], l["name"])
    print((l["error"] or "")[:1500])
    print()
