import inspect
from frappe.database.postgres import database as pd
src = inspect.getsource(pd.PostgresDatabase.modify_query)
print(src)
