F = "/workspace/frappe-bench/apps/erpnext/erpnext/accounts/report/purchase_register/purchase_register.py"
t = open(F).read()
old = 'case add_deduct_tax when "Add" then sum(base_tax_amount_after_discount_amount)'
new = "case add_deduct_tax when 'Add' then sum(base_tax_amount_after_discount_amount)"
assert old in t, "pattern not found"
t = t.replace(old, new, 1)
open(F,"w").write(t)
print("fixed purchase_register case when 'Add'")
import py_compile
try:
    py_compile.compile(F, doraise=True); print("SYNTAX OK")
except Exception as e:
    print("SYNTAX ERR", e)
