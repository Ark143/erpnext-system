# Revert test_loyalty_program.py (test files should not be patched)
import subprocess
F = "/workspace/frappe-bench/apps/erpnext/erpnext/accounts/doctype/loyalty_program/test_loyalty_program.py"
t = open(F).read()
if "coalesce(" in t:
    # restore ifnull( -> coalesce( is the only change we made; revert it
    t2 = t.replace("coalesce(", "ifnull(")
    open(F, "w").write(t2)
    print("reverted test_loyalty_program.py: coalesce->ifnull")
else:
    print("no coalesce in test file, nothing to revert")
