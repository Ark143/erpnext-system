F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/queries.py"
t = open(F).read()

old = "limit %(start)s, %(page_len)s"
new = "limit %(page_len)s offset %(start)s"
if old in t:
    t = t.replace(old, new, 1)
    print("patched LIMIT ->", new in t)
else:
    print("LIMIT not found")

oldv = '"start": start,'
newv = '"start": cint(start),'
if oldv in t:
    t = t.replace(oldv, newv, 1)
    print("patched start")

oldv2 = '"page_len": page_len,'
newv2 = '"page_len": cint(page_len),'
if oldv2 in t:
    t = t.replace(oldv2, newv2, 1)
    print("patched page_len")

open(F, "w").write(t)
print("final check offset:", "offset %(start)s" in t, "| cint(start):", "cint(start)" in t)
