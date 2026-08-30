import inspect
import erpnext.controllers.queries as q
src = inspect.getsource(q.item_query)
i = src.find(".format(")
print(src[i-400:i+400])
