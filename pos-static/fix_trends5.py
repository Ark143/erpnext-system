import re
F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()
# The data1 query has: t1.docstatus = 1 {} {}\n\t\t\t\t\tgroup by {}\n\t\t\t\t""".format(
# Replace that specific 'group by {}' occurrence (the one preceded by docstatus line) with augmented.
old = "t1.docstatus = 1 {} {}\n\t\t\t\t\tgroup by {}"
new = "t1.docstatus = 1 {} {}\n\t\t\t\t\tgroup by get_group_by_augmented(query_details, conditions[\"group_by\"])"
if old in t:
    t = t.replace(old, new, 1)
    print("patched data1 group by -> augmented")
else:
    print("NOT FOUND; context sample:")
    i = t.find("docstatus = 1")
    print(repr(t[i-10:i+80]))
open(F,"w").write(t)
