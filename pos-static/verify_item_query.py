import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
from erpnext.controllers.queries import item_query
# exercise the exact query path the UI uses
res = item_query("Item", "", "name", 0, 10,
                 filters={"is_sales_item":1, "customer":"DANILO OBRA", "has_variants":0}, as_dict=True)
print("item_query direct ->", len(res), "rows; first:", res[0].get("name") if res else None)
# also a customer with party-specific items path (empty lists ok)
res2 = item_query("Item", "wire", "name", 0, 10, filters={"is_sales_item":1}, as_dict=True)
print("item_query txt=wire ->", len(res2), "rows")
