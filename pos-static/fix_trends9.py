F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()
# line 148 currently: \tdata1 = frappe.db.sql(  (1 tab) -> needs 2 tabs
old = "\tgroup_by_aug = get_group_by_augmented(query_details, conditions[\"group_by\"])\n\tdata1 = frappe.db.sql("
new = "\t\tgroup_by_aug = get_group_by_augmented(query_details, conditions[\"group_by\"])\n\tdata1 = frappe.db.sql("
if old in t:
    t = t.replace(old, new, 1)
    print("fixed: data1 now 2 tabs")
else:
    print("pattern not found; trying just the data1 line")
    t = t.replace("\tdata1 = frappe.db.sql(", "\t\tdata1 = frappe.db.sql(", 1)
    print("replaced bare data1 line")
open(F,"w").write(t)
import py_compile
try:
    py_compile.compile(F, doraise=True)
    print("SYNTAX OK")
except Exception as e:
    print("SYNTAX ERR:", e)
