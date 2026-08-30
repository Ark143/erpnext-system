import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# Find the vehicle_pos web page and its content/route
for r in frappe.get_all("Web Page", filters={"route":"vehicle_pos"}, fields=["name","route","content","script","style","published"]):
    print("NAME:", r["name"])
    print("ROUTE:", r["route"], "PUBLISHED:", r.get("published"))
    print("--- SCRIPT (first 1500) ---")
    print((r.get("script") or "")[:1500])
    print("--- STYLE (first 800) ---")
    print((r.get("style") or "")[:800])
