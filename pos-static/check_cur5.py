import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
from erpnext.accounts.party import get_party_details
d = get_party_details("NELSON L. CASTILLO", "Customer", company="My Company", posting_date="2026-08-30")
print("party_details currency:", d.get("currency"))
print("currency-keys:", {k:v for k,v in d.items() if "currenc" in k.lower()})
