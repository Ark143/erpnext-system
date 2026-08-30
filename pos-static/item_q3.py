import inspect
import erpnext.controllers.queries as q
src = inspect.getsource(q.item_query)
i = src.find("return frappe.db.sql")
print(src[i-400:i+1100])
