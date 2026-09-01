import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
from erpnext.accounts.party import get_party_details
try:
    d = get_party_details("NELSON L. CASTILLO", "Customer", company="My Company", posting_date="2026-08-30")
    print("party_details currency:", d.get("currency"))
    print("party_details keys w/ currency:", {k:v for k,v in d.items() if "currenc" in k.lower()})
except Exception as e:
    import traceback; traceback.print_exc()
# customer's default receivable account + its currency
acc = frappe.db.get_value("Customer", "NELSON L. CASTILLO", "account")
print("customer account:", acc)
if acc:
    print("account currency:", frappe.db.get_value("Account", acc, "account_currency"))
# company default receivable account currency
cr = frappe.db.get_value("Company","My Company","default_receivable_account")
print("company recv acct:", cr, frappe.db.get_value("Account", cr, "account_currency") if cr else None)
