import os, re
F = "/workspace/frappe-bench/apps/frappe/frappe/database/postgres/database.py"
bak = F + ".bak_pre_patch"
if not os.path.exists(bak):
    open(bak, "w", encoding="utf-8").write(open(F, encoding="utf-8").read())
s = open(F, encoding="utf-8").read()
old = (
    '\tquery = str(query).replace("`", \'"\')\n'
    '\tquery = replace_locate_with_strpos(query)\n'
)
new = (
    '\tquery = str(query).replace("`", \'"\')\n'
    '\t# MariaDB -> PostgreSQL compatibility: CURDATE() is not a PostgreSQL function\n'
    '\tquery = re.sub(r"CURDATE\\s*\\(\\s*\\)", "CURRENT_DATE", query)\n'
    '\tquery = replace_locate_with_strpos(query)\n'
)
assert old in s, "modify_query anchor not found!"
s = s.replace(old, new, 1)
open(F, "w", encoding="utf-8").write(s)
print("PATCHED", F)
