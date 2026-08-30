import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
from erpnext.controllers.queries import item_query
try:
    res = item_query("Item", "", "name", 0, 10,
                     filters={"is_sales_item":1, "customer":"DANILO OBRA", "has_variants":0}, as_dict=True)
    print("OK results:", len(res))
except Exception as e:
    import traceback
    tb = traceback.format_exc()
    print(tb[-1500:])
