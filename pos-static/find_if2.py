import os, re
app = "/workspace/frappe-bench/apps/erpnext/erpnext"
sql_if = re.compile(r'\bif\s*\(\s*[a-z_][\w.]*\s*[<>!=]=\s*\d|if\s*\([^()]*[a-z_]\.[a-z_]|if\s*\(\s*\w+\s*,\s*\w+\s*,\s*\w+\s*\)')
real=[]
for root,_,files in os.walk(app):
    for fn in files:
        if not fn.endswith(".py"): continue
        p=os.path.join(root,fn); txt=open(p,encoding="utf-8",errors="ignore").read()
        for m in re.finditer(r'if\s*\(', txt):
            i=m.start(); line=txt[max(0,txt.rfind("\n",0,i)+1):txt.find("\n",i)]
            low=line.lower()
            if any(k in low for k in ["select","from ","where ","sum(","frappe.db.sql","execute(","case when","qty","amount","balance","debit","credit","group by","order by","join "]):
                real.append((os.path.relpath(p,app), txt[max(0,i-40):i+60].replace("\n"," ")))
print("POSSIBLE SQL if():", len(real))
for r in real: print(r[0], "::", r[1])
