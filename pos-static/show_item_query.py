import inspect, frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
import erpnext.controllers.queries as q
src = inspect.getsource(q.item_query)
print(src)
