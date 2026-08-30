import glob, os
d="/workspace/frappe-bench/sites/assets/frappe/dist/js"
for pat in ["frappe-web.bundle.*.js","bootstrap-4-web.bundle.*.js"]:
    for f in glob.glob(os.path.join(d,pat)):
        s=open(f,encoding="utf-8",errors="ignore").read()
        print(f"{os.path.basename(f)}")
        print(f"  fn.dropdown={s.count('fn.dropdown =')}  class Dropdown={s.count('class Dropdown')}  jquery-bootstrap={s.count('jquery-bootstrap')}  size={len(s)}")
