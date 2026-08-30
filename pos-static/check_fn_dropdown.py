import glob, os, re
d="/workspace/frappe-bench/sites/assets/frappe/dist/js"
f=sorted(glob.glob(os.path.join(d,"bootstrap-4-web.bundle.*.js")))[-1]
s=open(f,encoding="utf-8",errors="ignore").read()
# bootstrap 4 attaches: $.fn.dropdown = ... ; look for fn.dropdown= or fn.dropdown =
for m in re.finditer(r'\.fn\.dropdown\s*=', s):
    print("FOUND $.fn.dropdown attach at", m.start(), "->", s[m.start():m.start()+60].replace("\n"," "))
if not list(re.finditer(r'\.fn\.dropdown\s*=', s)):
    # also check for noConflict / Constructor pattern
    print("fn.dropdown= not found; checking for Dropdown interface markers:")
    for kw in ["Dropdown._jQueryInterface","_jQueryInterface","noConflict","Constructor"]:
        print(" ", kw, s.count(kw))
