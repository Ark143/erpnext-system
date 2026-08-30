F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()

# 1) Fix indentation of the injected group_by_aug line (1 tab -> 2 tabs)
if "\tgroup_by_aug = get_group_by_augmented" in t:
    t = t.replace("\tgroup_by_aug = get_group_by_augmented(query_details, conditions[\"group_by\"])",
                  "\t\tgroup_by_aug = get_group_by_augmented(query_details, conditions[\"group_by\"])", 1)
    print("indented group_by_aug")

# 2) Change data1 format arg from conditions["group_by"] to group_by_aug
# The data1 .format() ends with: ... cond,\n\t\t\t\t\tconditions["group_by"],\n\t\t\t\t),
old = '\t\t\t\t\tcond,\n\t\t\t\t\tconditions["group_by"],\n\t\t\t\t),'
new = '\t\t\t\t\tcond,\n\t\t\t\t\tgroup_by_aug,\n\t\t\t\t),'
if old in t:
    t = t.replace(old, new, 1)
    print("data1 format arg -> group_by_aug")
else:
    print("data1 format arg NOT FOUND (trying alt)")
    # alt: the group-by arg is the 11th format positional; find 'conditions["group_by"],' just before '),' after cond
    t2 = t.replace('\t\t\t\t\tconditions["group_by"],\n\t\t\t\t),', '\t\t\t\t\tgroup_by_aug,\n\t\t\t\t),', 1)
    if t2 != t:
        t = t2; print("alt replaced")

# 3) Also fix the 'row' query (line ~230) group by similarly
old_row = '\t\t\t\t\t\tand t1.docstatus = 1 and {} = {} {} {}\n\t\t\t\t\t\tgroup by {},'
new_row = '\t\t\t\t\t\tand t1.docstatus = 1 and {} = {} {} {}\n\t\t\t\t\t\tgroup by get_group_by_augmented(query_details, {}),'
# row query uses sel_col; its group by should be sel_col (the distinct col), not augmented. Leave as-is (it's DISTINCT on sel_col).
# Actually row query: select DISTINCT(sel_col) ... group by {} -> conditions["group_by"]; sel_col == group_by so fine.

open(F,"w").write(t)
print("written")
# syntax check
import py_compile
try:
    py_compile.compile(F, doraise=True)
    print("SYNTAX OK")
except Exception as e:
    print("SYNTAX ERR:", e)
