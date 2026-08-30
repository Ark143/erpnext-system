import os, re
app = "/workspace/frappe-bench/apps/erpnext/erpnext"
# Find raw-SQL report/query files with MySQL-isms
pat_if = re.compile(r"\bif\s*\(\s*[a-z_][\w.]*\s*[<>=!]")  # if( with comparison/cond -> SQL if()
pat_ifnull = re.compile(r"\bifnull\s*\(")
pat_locate = re.compile(r"\blocate\s*\(")
pat_zero = re.compile(r"'0000-00-00'")
hits = []
for root,_,files in os.walk(app):
    for fn in files:
        if not fn.endswith(".py"): continue
        p = os.path.join(root, fn)
        try:
            src = open(p, encoding="utf-8", errors="ignore").read()
        except: continue
        # only care about files that build SQL (heuristic: contain frappe.db.sql or query strings)
        if "frappe.db.sql" not in src and "query =" not in src and ".format(" not in src:
            continue
        c = {"if": len(pat_if.findall(src)), "ifnull": len(pat_ifnull.findall(src)),
             "locate": len(pat_locate.findall(src)), "zero": len(pat_zero.findall(src))}
        if sum(c.values()) > 0:
            rel = p.replace(app+"/", "")
            hits.append((rel, c))
print(f"FILES WITH MYSQL-ISMS (SQL-building): {len(hits)}")
for rel, c in sorted(hits, key=lambda x: -sum(x[1].values())):
    print(f"  {rel}: if={c['if']} ifnull={c['ifnull']} locate={c['locate']} zero={c['zero']}")
