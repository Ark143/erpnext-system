import re
# Check frappe postgres modify_query for ifnull/locate/if handling
F = "/workspace/frappe-bench/apps/frappe/frappe/database/postgres/database.py"
t = open(F).read()
for kw in ["ifnull", "locate", "strpos", "coalesce", "def modify_query"]:
    idx = t.find(kw)
    print(f"{kw}: {'FOUND' if idx>=0 else 'absent'}")
# show the modify_query function body snippet
i = t.find("def modify_query")
print("\n--- modify_query body (first 1200 chars) ---")
print(t[i:i+1200])
