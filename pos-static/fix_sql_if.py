import re
# Fix stock/stock_balance.py
F1 = "/workspace/frappe-bench/apps/erpnext/erpnext/stock/stock_balance.py"
t1 = open(F1).read()
old1 = "if(dont_reserve_qty_on_return, so_item_returned_qty, 0)"
new1 = "case when dont_reserve_qty_on_return then so_item_returned_qty else 0 end"
assert old1 in t1, "stock_balance old not found"
t1 = t1.replace(old1, new1)
open(F1,"w").write(t1)
print("stock_balance.py patched:", new1 in t1)

# Fix payment_entry.py (3 SQL if( occurrences)
F2 = "/workspace/frappe-bench/apps/erpnext/erpnext/accounts/doctype/payment_entry/payment_entry.py"
t2 = open(F2).read()
old2 = "if({rounded_total_field}, {rounded_total_field}, {grand_total_field})"
new2 = "case when {rounded_total_field} then {rounded_total_field} else {grand_total_field} end"
n = t2.count(old2)
assert n>0, "payment_entry old not found"
t2 = t2.replace(old2, new2)
open(F2,"w").write(t2)
print("payment_entry.py patched occurrences:", n)

# also generic: any other SQL if( with numeric/field args in these two already covered.
print("done")
