import os, re
app = "/workspace/frappe-bench/apps/erpnext/erpnext"
hits=[]
for root,_,files in os.walk(app):
    for fn in files:
        if not fn.endswith(".py"): continue
        p=os.path.join(root,fn)
        txt=open(p,encoding="utf-8",errors="ignore").read()
        # find if( inside string literals that look like SQL: preceded by select/where/from or containing sql-ish tokens
        for m in re.finditer(r'if\s*\(', txt):
            i=m.start()
            ctx=txt[max(0,i-60):i+80].lower()
            # crude SQL heuristic
            if any(k in ctx for k in ["select","from","where","sum(","case","qty","amount","balance",","]):
                hits.append((os.path.relpath(p,app), i, txt[max(0,i-50):i+70].replace("\n"," ")))
print("SQL-ish if( candidates:", len(hits))
for h in hits[:40]:
    print(h[0], "::", h[2])
