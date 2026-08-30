F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()

# 1) Fix line 147 over-indent: 3 tabs -> 2 tabs
bad = "\t\t\tgroup_by_aug = get_group_by_augmented(query_details, conditions[\"group_by\"])"
good = "\t\tgroup_by_aug = get_group_by_augmented(query_details, conditions[\"group_by\"])"
if bad in t:
    t = t.replace(bad, good, 1)
    print("fixed group_by_aug indent (3->2 tabs)")
else:
    print("3-tab form NOT FOUND; current forms:")
    import re as _re
    for m in _re.finditer(r"[^\n]*group_by_aug[^\n]*", t):
        print(repr(m.group(0)))

# 2) Fix data1 .format() last arg: conditions["group_by"] -> group_by_aug
# The data1 format call: ... cond,\n\t\t\t\tconditions["group_by"],\n\t\t\t),
old = '\t\t\t\tcond,\n\t\t\t\tconditions["group_by"],\n\t\t\t),'
new = '\t\t\t\tcond,\n\t\t\t\tgroup_by_aug,\n\t\t\t),'
if old in t:
    t = t.replace(old, new, 1)
    print("data1 format arg -> group_by_aug")
else:
    print("data1 format arg pattern NOT FOUND; trying line-164 direct")
    t = t.replace('\t\t\t\tconditions["group_by"],\n\t\t\t),', '\t\t\t\tgroup_by_aug,\n\t\t\t),', 1)
    print("applied direct replace")

open(F,"w").write(t)
import py_compile
try:
    py_compile.compile(F, doraise=True)
    print("SYNTAX OK")
except Exception as e:
    print("SYNTAX ERR:", e)
