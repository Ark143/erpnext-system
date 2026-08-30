import re
F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()

# 1) Fix helper to exclude columns that appear inside aggregates (SUM/CASE)
helper_old = '''def get_group_by_augmented(query_details, base_group_by):
\t"""PostgreSQL requires all non-aggregated SELECT columns in GROUP BY.
\tMySQL allows loose grouping; this augments the base group_by with the
\tother bare table.column refs selected in query_details."""
\tcols = set(re.findall(r"`?t\\d+`?\\.`?\\w+`?", query_details))
\taug = [base_group_by] + sorted(c for c in cols if c != base_group_by)
\treturn ", ".join(aug)'''
helper_new = '''def get_group_by_augmented(query_details, base_group_by):
\t"""PostgreSQL requires all non-aggregated SELECT columns in GROUP BY.
\tMySQL allows loose grouping; this augments the base group_by with the
\tother bare table.column refs selected in query_details (excluding those
\tthat only appear inside aggregate functions like SUM(...))."""
\t# columns that appear anywhere inside SUM(...) / aggregate -> skip
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
\treturn ", ".join([base_group_by] + aug)'''
if helper_old in t:
    t = t.replace(helper_old, helper_new, 1)
    print("helper improved")
else:
    print("helper_old NOT FOUND")

# 2) data1: replace literal function call with precomputed arg
# Remove the function-call text in SQL
t = t.replace(
    "\t\t\t\t\tgroup by get_group_by_augmented(query_details, conditions[\"group_by\"])",
    "\t\t\t\t\tgroup by {}",
)
# Add precomputed variable before data1 query and pass as format arg.
# Find the data1 frappe.db.sql block and inject the variable + replace last format arg.
marker = '\tdata1 = frappe.db.sql('
if marker in t:
    # insert augmented var just before data1
    t = t.replace(marker, '\tgroup_by_aug = get_group_by_augmented(query_details, conditions["group_by"])\n' + marker, 1)
    print("data1 var injected")
# replace the data1 format() last arg `conditions["group_by"],` -> `group_by_aug,`
# The data1 format call ends with: cond,\n\t\t\t\t\tconditions["group_by"],\n\t\t\t),
old_arg = '\t\t\t\t\tcond,\n\t\t\t\t\tconditions["group_by"],\n\t\t\t),'
new_arg = '\t\t\t\t\tcond,\n\t\t\t\t\tgroup_by_aug,\n\t\t\t),'
if old_arg in t:
    t = t.replace(old_arg, new_arg, 1)
    print("data1 format arg replaced")
else:
    print("data1 format arg NOT FOUND")

open(F,"w").write(t)
print("done")
