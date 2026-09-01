import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
print("default co currency:", frappe.db.get_value("Company", "My Company", "default_currency"))
print("enabled currencies:", [c["name"] for c in frappe.get_all("Currency", filters={"enabled":1}, fields=["name"])])
# how many customers have USD default
print("USD customers:", frappe.db.count("Customer", {"default_currency":"USD"}))
print("PHP customers:", frappe.db.count("Customer", {"default_currency":"PHP"}))
print("null-currency customers:", frappe.db.count("Customer", {"default_currency":["in",["","NULL"]]}))
# exchange rate USD->PHP?
ex = frappe.db.sql("SELECT * FROM `tabCurrency Exchange` WHERE from_currency='USD' AND to_currency='PHP' ORDER BY date DESC LIMIT 1", as_dict=1)
print("USD->PHP rate:", ex)
