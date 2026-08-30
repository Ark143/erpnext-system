import re
F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()
if "import re" not in t:
    t = t.replace("import frappe\n", "import re\nimport frappe\n", 1)
    print("added import re")
else:
    print("re already imported")
open(F,"w").write(t)
