F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()
# Force group_by_aug to exactly 2 tabs
t = t.replace("\t\t\tgroup_by_aug = get_group_by_augmented(query_details, conditions[\"group_by\"])",
              "\t\tgroup_by_aug = get_group_by_augmented(query_details, conditions[\"group_by\"])")
# Force data1 = to exactly 2 tabs
t = t.replace("\tdata1 = frappe.db.sql(", "\t\tdata1 = frappe.db.sql(")
# Verify no 1-tab or 3-tab stray versions remain
import re
leftover = re.findall(r"\n[^\n]*group_by_aug[^\n]*|\n[^\n]*data1 = frappe.db.sql\(", t)
# Also fix any other occurrences of data1 at wrong indent (the injection may have duplicated)
print("group_by_aug occurrences:", t.count("group_by_aug = get_group_by_augmented"))
open(F,"w").write(t)
import py_compile
try:
    py_compile.compile(F, doraise=True)
    print("SYNTAX OK")
except Exception as e:
    print("SYNTAX ERR:", e)
