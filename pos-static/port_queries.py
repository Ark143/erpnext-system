import re
F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/queries.py"
t = open(F).read()
orig = t
reps = 0

# 1) ifnull( -> coalesce(
n = t.count("ifnull(")
t = t.replace("ifnull(", "coalesce(")
reps += n

# 2) '0000-00-00' zero-date -> '0001-01-01' (postgres rejects 0000 date)
n2 = t.count("'0000-00-00'")
t = t.replace("'0000-00-00'", "'0001-01-01'")
reps += n2

# 3) backtick `tabX` -> "tabX"
def bt(m):
    return '"' + m.group(1) + '"'
t, n3 = re.subn(r'`(tab[^`]+)`', lambda m: '"'+m.group(1)+'"', t)
reps += n3

# 4) MySQL if(ternary) in SQL: if(cond, a, b) -> case when cond then a else b end
#    handle: if(locate(...), x, y) and if(expr, a, b) generally
def if_ternary(m):
    inner = m.group(1)
    a = m.group(2); b = m.group(3)
    return "(case when %s then %s else %s end)" % (inner, a, b)
# match if( ... , ... , ... ) with balanced parens for first arg
pat = re.compile(r'\bif\(\s*((?:[^(),]|\([^)]*\))*?)\s*,\s*((?:[^(),]|\([^)]*\))*?)\s*,\s*((?:[^()]|\([^)]*\))*?)\s*\)')
t, n4 = pat.subn(if_ternary, t)
reps += n4

open(F, "w").write(t)
print("replacements: ifnull=%d zerodate=%d backtick=%d if-ternary=%d  total_changed=%s" % (n, n2, n3, n4, t!=orig))
# sanity: ensure no remaining easy markers
print("remaining ifnull:", t.count("ifnull("), "remaining `tab:", len(re.findall(r'`tab', t)), "remaining 0000-00-00:", t.count("'0000-00-00'"))
