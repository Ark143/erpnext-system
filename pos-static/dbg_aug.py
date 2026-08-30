import frappe, re
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
from erpnext.controllers.trends import get_columns, get_group_by_augmented
filters = frappe._dict({"company":"ULTRA MRF","based_on":"Item","period":"Monthly","fiscal_year":frappe.defaults.get_global_default("fiscal_year")})
c = get_columns(filters, "Sales Order")
qd = c["based_on_select"] + c["period_wise_select"]
print("augmented group by:", get_group_by_augmented(qd, c["group_by"]))
