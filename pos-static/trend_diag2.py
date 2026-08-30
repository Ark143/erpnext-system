import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# Is there a default company? (the trend report needs it)
gc = frappe.defaults.get_global_default("company")
print("global_default company:", gc)
uc = frappe.defaults.get_user_default("company", "Administrator")
print("user_default company (Administrator):", uc)
comps = frappe.get_all("Company", pluck="name")
print("Companies in DB:", comps)
# Does the report fail because no company default? Try running it with company explicitly
from erpnext.controllers.trends import get_columns
try:
    cols = get_columns(frappe._dict({"company":"ULTRA MRF","based_on":"Item","from_date":"2026-01-01","to_date":"2026-12-31"}), "Sales Order")
    print("get_columns WITH company -> OK, cols:", len(cols) if isinstance(cols,(list,tuple)) else cols)
except Exception as e:
    print("get_columns WITH company -> ERR:", type(e).__name__, str(e)[:80])
