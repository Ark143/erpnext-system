import os, re
app = "/workspace/frappe-bench/apps/erpnext/erpnext"
# ONLY the breaking pattern: `when "X"` (double-quoted value in a CASE) inside SQL strings.
pat = re.compile(r'when\s+"([^"]+)"')
# also `case when "X"` and `<col> = "X"` inside a triple-quoted SQL string is hard to isolate;
# focus on `when "X"` which is unambiguous CASE value literal.
hits = []
for root,_,files in os.walk(app):
    for fn in files:
        if not fn.endswith(".py") or fn.startswith("test_"): continue
        p = os.path.join(root, fn)
        try: src = open(p, encoding="utf-8", errors="ignore").read()
        except: continue
        if "frappe.db.sql" not in src and ".format(" not in src: continue
        for m in pat.finditer(src):
            # get surrounding line
            line_start = src.rfind("\n", 0, m.start())+1
            line = src[line_start:src.find("\n", m.start())]
            hits.append((p.replace(app+"/",""), m.group(1), line.strip()[:80]))
print(f"CASE WHEN \"VALUE\" HITS: {len(hits)}")
for rel, val, ctx in hits:
    print(f"  {rel}: when \"{val}\"  | {ctx}")
