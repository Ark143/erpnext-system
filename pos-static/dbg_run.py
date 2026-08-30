import frappe, re
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
from erpnext.controllers import trends
# monkeypatch get_data to print the group_by used
orig = trends.get_data
def patched(filters, conditions):
    qd = conditions["based_on_select"] + conditions["period_wise_select"]
    print("AUG RESULT:", trends.get_group_by_augmented(qd, conditions["group_by"]))
    return orig(filters, conditions)
trends.get_data = patched
import erpnext.selling.report.sales_order_trends.sales_order_trends as sot
sot.get_data = patched
filters = frappe._dict({"company":"ULTRA MRF","based_on":"Item","period":"Monthly","fiscal_year":frappe.defaults.get_global_default("fiscal_year")})
try:
    res = sot.execute(filters)
    print("OK rows:", len(res[0]) if isinstance(res,tuple) else "n/a")
except Exception as e:
    print("ERR:", type(e).__name__, str(e)[:120])
