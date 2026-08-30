F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/queries.py"
t = open(F).read()
old = 'or coalesce("tabItem".end_of_life, \'0000-00-00\')=\'0000-00-00\')'
new = 'or coalesce("tabItem".end_of_life, \'0001-01-01\')=\'0001-01-01\')'
if old in t:
    t = t.replace(old, new, 1)
    print("patched end_of_life sentinel")
else:
    print("NOT FOUND; current snippet:")
    i = t.find("end_of_life")
    print(t[i-30:i+90])
open(F, "w").write(t)
