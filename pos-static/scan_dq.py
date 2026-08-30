import os, re
app = "/workspace/frappe-bench/apps/erpnext/erpnext"
# find double-quoted string LITERALS used as values inside SQL (case when "X", = "X", in ("X"))
# Heuristic: `"` that is NOT followed by `tab` (legit table identifier) and appears in a sql-ish context.
pat = re.compile(r'(when|in|=|!=|<>)\s+"([^"]+)"')
hits = []
for root,_,files in os.walk(app):
    for fn in files:
        if not fn.endswith(".py") or fn.startswith("test_"): continue
        p = os.path.join(root, fn)
        try: src = open(p, encoding="utf-8", errors="ignore").read()
        except: continue
        if "frappe.db.sql" not in src and ".format(" not in src: continue
        for m in pat.finditer(src):
            # exclude legit column-ish? we want value literals. Show context.
            hits.append((p.replace(app+"/",""), m.group(0), m.start()))
print(f"DOUBLE-QUOTED VALUE-LITERAL HITS: {len(hits)}")
for rel, txt, pos in hits[:60]:
    print(f"  {rel}: ...{txt}...")
