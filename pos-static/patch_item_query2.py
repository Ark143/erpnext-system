F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/queries.py"
t = open(F).read()
orig = t

# 1) Quote all tabItem. column-prefix references (only used inside item_query)
t = t.replace("tabItem.", '"tabItem".')

# 2) Backtick-quoted table in the subquery -> double quotes
t = t.replace("`tabItem Barcode`", '"tabItem Barcode"')

# 3) MySQL ifnull -> postgres coalesce (item_query uses it on end_of_life)
t = t.replace("ifnull(", "coalesce(")

# 4) Description conditional: if(length(...)>40, concat(...), description)
old_desc = ('if(length("tabItem".description) > 40, '
            'concat(substr("tabItem".description, 1, 40), "..."), description)')
new_desc = ('case when length("tabItem".description) > 40 '
            "then concat(substr(\"tabItem\".description, 1, 40), '...') "
            'else description end')
if old_desc in t:
    t = t.replace(old_desc, new_desc, 1)
    print("patched description conditional")
else:
    print("WARN description conditional not matched")

# 5) ORDER BY if(locate(...), locate(...), 99999) -> case when ... then ... else ... end
import re
def repl_locate(m):
    inner = m.group(1)  # e.g. %(_txt)s, name
    return ('(case when locate(' + inner + ') > 0 then locate(' + inner +
            ') else 99999 end)')
# match: if(locate(EXPR), locate(EXPR), 99999)
pat = re.compile(r'if\(locate\(([^)]*)\),\s*locate\([^)]*\),\s*99999\)')
new_t, n = pat.subn(repl_locate, t)
t = new_t
print("patched order-by locate clauses:", n)

# 6) Ensure LIMIT uses offset form (already done earlier, but keep idempotent)
t = t.replace("limit %(start)s, %(page_len)s", "limit %(page_len)s offset %(start)s")

open(F, "w").write(t)
print("changed:", t != orig)
print("contains case-when-locate:", "case when locate" in t)
print("contains tabItem. unquoted:", "tabItem." in t and '"tabItem".' not in t)
