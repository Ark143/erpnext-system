import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
profiles = frappe.get_all("POS Profile", fields=["name","company","currency","disabled"])
print("PROFILES:", profiles)
# company default currency
for c in frappe.get_all("Company", filters={"is_group":0}, fields=["name","default_currency"]):
    print("CO:", c)
