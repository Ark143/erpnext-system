import re
F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()

# Find the data1 query group by line and enhance it
old = '''\t\t\t\t\tgroup by {}\n\t\t\t\t""".format(\n\t\t\t\tquery_details,\n\t\t\t\tconditions["trans"],\n\t\t\t\tconditions["trans"],\n\t\t\t\tconditions["addl_tables"],\n\t\t\t\t"%s",\n\t\t\t\tposting_date,\n\t\t\t\t"%s",\n\t\t\t\t"%s",\n\t\t\t\tconditions.get("addl_tables_relational_cond"),\n\t\t\t\tcond,\n\t\t\t\tconditions["group_by"],\n\t\t\t),'''

# We replace the group-by argument with an augmented one. Use a regex on the format() args.
# Simpler: replace `conditions["group_by"],` (last arg before close) in data1 with augmented expression.
# But there are two queries (data1 and the DISTINCT row query). Target data1 specifically by the preceding context.
old_groupby_arg = '\t\t\t\t\tcond,\n\t\t\t\tconditions["group_by"],\n\t\t\t),'
new_groupby_arg = '''\t\t\t\t\tcond,
\t\t\t\tget_group_by_augmented(query_details, conditions["group_by"]),
\t\t\t),'''

if old_groupby_arg in t:
    t = t.replace(old_groupby_arg, new_groupby_arg, 1)
    print("patched data1 group by arg")
else:
    print("data1 groupby arg NOT FOUND")

# Add helper function near top (after imports)
helper = '''\n\ndef get_group_by_augmented(query_details, base_group_by):
\t"""PostgreSQL requires all non-aggregated SELECT columns in GROUP BY.
\tMySQL allows loose grouping; this augments the base group_by with the
\tother bare table.column refs selected in query_details."""
\tcols = set(re.findall(r"`?t\\d+`?\\.`?\\w+`?", query_details))
\taug = [base_group_by] + sorted(c for c in cols if c != base_group_by)
\treturn ", ".join(aug)\n\n'''
# insert helper before get_columns
if "def get_group_by_augmented" not in t:
    t = t.replace("def get_columns(filters, trans):", helper + "def get_columns(filters, trans):", 1)
    print("helper added")

open(F,"w").write(t)
print("done")
