import glob, os
d="/workspace/frappe-bench/sites/assets/frappe/dist/js"
for pat in ["bootstrap-4-web.bundle.*.js"]:
    for f in sorted(glob.glob(os.path.join(d,pat))):
        s=open(f,encoding="utf-8",errors="ignore").read()
        for kw in ["dropdown", "Dropdown", "bs.dropdown", "data-toggle", "show.bs.dropdown", "jquery-bootstrap"]:
            print(f"{kw}: {s.count(kw)}")
        # print a snippet around first 'dropdown' occurrence
        i=s.lower().find("dropdown")
        if i>0:
            print("SNIPPET:", s[i-60:i+120].replace("\n"," "))
