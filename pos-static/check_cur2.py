import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
print("NELSON default_currency:", frappe.db.get_value("Customer", "NELSON L. CASTILLO", "default_currency"))
print("JOEPET default_currency:", frappe.db.get_value("Customer", "JOEPET G DAVID", "default_currency"))
# any non-null default_currency at all?
rows = frappe.db.sql("SELECT default_currency, COUNT(*) c FROM tabCustomer WHERE default_currency IS NOT NULL AND default_currency <> '' GROUP BY default_currency", as_dict=1)
print("non-null currencies:", rows)
# Customer Vehicle NDB-3344 customer + currency
print("NDB-3344:", frappe.db.get_value("Customer Vehicle", "NDB-3344", ["customer","default_currency"]))
