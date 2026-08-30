import inspect
import erpnext.controllers.queries as q
src = inspect.getsource(q.item_query)
print(src)
