import os, glob
d="/workspace/frappe-bench/sites/assets/frappe/dist/js"
for f in sorted(glob.glob(d+"/*.js")):
    try:
        s=open(f,encoding="utf-8",errors="ignore").read()
    except: 
        continue
    dd = s.count("fn.dropdown =")
    cap = s.count("class Dropdown")
    if dd or cap:
        print(f"{os.path.basename(f):<45} fn.dropdown={dd} DropdownClass={cap}")
