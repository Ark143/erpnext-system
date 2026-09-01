import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
for c in frappe.get_all("Company", filters={"is_group":0}, fields=["name"]):
    co = c["name"]
    acc = frappe.db.get_value("Company", co, "default_receivable_account")
    cur = frappe.db.get_value("Account", acc, "account_currency") if acc else None
    print(f"{co:35s} recv_acct={acc} currency={cur}")
