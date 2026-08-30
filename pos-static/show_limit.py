import inspect
import erpnext.controllers.queries as q
src = inspect.getsource(q.item_query)
i = src.find("limit")
print(src[i-200:i+120])
print("---- exact limit line ----")
for line in src.splitlines():
    if "limit" in line.lower():
        print(repr(line))
