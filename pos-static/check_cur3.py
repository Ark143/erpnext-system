import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# does tabCustomer have default_currency column?
cols = frappe.db.sql("SELECT column_name FROM information_schema.columns WHERE table_name='tabCustomer' AND column_name='default_currency'", as_dict=1)
print("tabCustomer.default_currency col:", cols)
if cols:
    for c in ["NELSON L. CASTILLO","JOEPET G DAVID"]:
        print(c, "->", frappe.db.get_value("Customer", c, "default_currency"))
# The POS Invoice currency used: company currency
print("company currency:", frappe.db.get_value("Company","My Company","default_currency"))
# where does erpnext decide USD? check get_party_details path: maybe from Customer's 'currency' field?
print("NELSON full currency-ish fields:", frappe.db.sql("SELECT name, default_currency FROM tabCustomer WHERE name='NELSON L. CASTILLO'", as_dict=1))
