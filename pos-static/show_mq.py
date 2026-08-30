import re
p = "/workspace/bench/apps/frappe/frappe/database/postgres/database.py"
t = open(p).read()
i = t.find("def modify_query")
print(t[i:i+1200])
