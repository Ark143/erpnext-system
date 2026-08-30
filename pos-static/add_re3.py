F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()
# Ensure import re exists at module top
if not t.lstrip().startswith("import re") and "\nimport re\n" not in t and "import re\n" not in t:
    # insert after the license comment block (first blank-ish line after copyright)
    t = "import re\n" + t
    open(F,"w").write(t)
    print("import re added at top")
else:
    print("re already there")
# verify
print("has import re:", "import re" in open(F).read())
