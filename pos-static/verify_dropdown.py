import glob, os
d="/workspace/frappe-bench/sites/assets/frappe/dist/js"
found=False
for pat in ["frappe-web.bundle.*.js","bootstrap-4-web.bundle.*.js"]:
    for f in sorted(glob.glob(os.path.join(d,pat))):
        s=open(f,encoding="utf-8",errors="ignore").read()
        dd=s.count("fn.dropdown =")
        cd=s.count("class Dropdown")
        jb=s.count("jquery-bootstrap")
        print(f"{os.path.basename(f)} size={len(s)} fn.dropdown={dd} class_Dropdown={cd} jquery_bootstrap={jb}")
        if dd>0: found=True
print("DROPDOWN_PLUGIN_PRESENT:", found)
