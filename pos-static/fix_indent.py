F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()
# the injected line is at 1 tab; must be 2 tabs
if "\tgroup_by_aug = get_group_by_augmented(query_details, conditions[\"group_by\"])\n\tdata1 = frappe.db.sql(" in t:
    t = t.replace(
        "\tgroup_by_aug = get_group_by_augmented(query_details, conditions[\"group_by\"])\n\tdata1 = frappe.db.sql(",
        "\t\tgroup_by_aug = get_group_by_augmented(query_details, conditions[\"group_by\"])\n\tdata1 = frappe.db.sql(",
        1,
    )
    print("fixed group_by_aug -> 2 tabs")
else:
    print("pattern not found; current:")
    import re as _r
    for m in _r.finditer(r"[^\n]*group_by_aug[^\n]*", t):
        print(repr(m.group(0)))
open(F,"w").write(t)
import py_compile
try:
    py_compile.compile(F, doraise=True)
    print("SYNTAX OK")
except Exception as e:
    print("SYNTAX ERR:", e)
