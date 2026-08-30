import re
F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()

# 1) import re at top
if not t.startswith("import re") and "import re\n" not in t:
    t = "import re\n" + t

# 2) SUM(IF(cond, col, NULL)) -> SUM(CASE WHEN cond THEN col ELSE NULL END)
def to_case(m):
    inner = m.group(1).strip()
    col = m.group(2).strip()
    return f"SUM(CASE WHEN {inner} THEN {col} ELSE NULL END)"
t = re.sub(r"SUM\(IF\(([^,]+?),\s*([^,]+?),\s*NULL\)\)", to_case, t)
print("SUM(IF) replaced:", len(re.findall(r"SUM\(CASE WHEN", t)))

# 3) add helper after the license/imports, before first def
helper = '''\n\ndef get_group_by_augmented(query_details, base_group_by):
\t"""PostgreSQL requires all non-aggregated SELECT columns in GROUP BY.
\tMySQL allows loose grouping; augment base group_by with the other
\tbare table.column refs selected in query_details (excluding those that
\tonly appear inside aggregate functions like SUM(...))."""
\tagg_cols = set(re.findall(r"(?:SUM|MAX|MIN|AVG|COUNT)\\(\\s*(?:DISTINCT\\s+)?([^)]*)\\)", query_details))
\tagg_tokens = set()
\tfor a in agg_cols:
\t\tagg_tokens.update(re.findall(r"t\\d+\\.\\w+", a))
\tall_cols = re.findall(r"t\\d+\\.\\w+", query_details)
\taug = []
\tfor c in all_cols:
\t\tif c == base_group_by or c in agg_tokens:
\t\t\tcontinue
\t\tif c not in aug:
\t\t\taug.append(c)
\treturn ", ".join([base_group_by] + aug)\n\n'''
t = t.replace("def get_columns(filters, trans):", helper + "def get_columns(filters, trans):", 1)

# 4) In get_data: inject group_by_aug before data1 query and use it.
# data1 query block starts with: \tdata1 = frappe.db.sql(
t = t.replace(
    '\tdata1 = frappe.db.sql(',
    '\tgroup_by_aug = get_group_by_augmented(query_details, conditions["group_by"])\n\tdata1 = frappe.db.sql(',
    1,
)
# data1 format: change last arg conditions["group_by"], -> group_by_aug,
t = t.replace(
    '\t\t\t\tcond,\n\t\t\t\tconditions["group_by"],\n\t\t\t),',
    '\t\t\t\tcond,\n\t\t\t\tgroup_by_aug,\n\t\t\t),',
    1,
)
# else-branch (no group_by) query: its group by {} also references conditions["group_by"] -> augment too
# The else-branch format ends with: conditions["group_by"],\n\t\t\t),
t = t.replace(
    '\t\t\t\tcond,\n\t\t\t\tconditions.get("addl_tables_relational_cond", ""),\n\t\t\t\tconditions["group_by"],\n\t\t\t),',
    '\t\t\t\tcond,\n\t\t\t\tconditions.get("addl_tables_relational_cond", ""),\n\t\t\t\tget_group_by_augmented(query_details, conditions["group_by"]),\n\t\t\t),',
    1,
)

open(F, "w").write(t)
import py_compile
try:
    py_compile.compile(F, doraise=True)
    print("SYNTAX OK")
except Exception as e:
    print("SYNTAX ERR:", e)
