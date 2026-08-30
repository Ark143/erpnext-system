import inspect
import erpnext.controllers.queries as q
src = inspect.getsource(q.item_query)
# print from the SQL query start
i = src.find("return frappe.db.sql")
print(src[i:i+1400])
