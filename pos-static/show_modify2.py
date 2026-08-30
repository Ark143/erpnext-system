import inspect
from frappe.database.postgres import database as pd
# find modify_query wherever it is
for cls in pd.PostgresDatabase.__mro__:
    if "modify_query" in cls.__dict__:
        print("defined in:", cls)
        print(inspect.getsource(cls.modify_query))
        break
else:
    print("modify_query not found in MRO; methods:")
    print([m for m in dir(pd.PostgresDatabase) if "query" in m.lower() or "modify" in m.lower()])
