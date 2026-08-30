F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()
if "import re" not in t:
    # add after the other imports, before `import erpnext`
    t = t.replace("import erpnext\n", "import re\nimport erpnext\n", 1)
    print("added import re")
else:
    print("re already present")
open(F,"w").write(t)
