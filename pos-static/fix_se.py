F = "/workspace/frappe-bench/apps/erpnext/erpnext/stock/doctype/stock_entry/stock_entry.py"
t = open(F).read()
old = "\t\t\tif d.secondary_item_type and flt(d.transfer_qty) == 0:"
new = "\t\t\tif getattr(d, 'secondary_item_type', None) and flt(d.transfer_qty) == 0:"
assert old in t, "anchor not found"
t = t.replace(old, new)
open(F,"w").write(t)
print("patched secondary_item_type guard:", new in t)
