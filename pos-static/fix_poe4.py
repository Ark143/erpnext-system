p = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/doctype/vehicle_pos_invoice/vehicle_pos_invoice.py"
s = open(p, encoding="utf-8").read()
old = (
'\t\t\t{"user": user, "status": "Open", "docstatus": 1},\n'
'\t\t\t["name", "pos_profile"],\n'
'\t\t)\n'
'\t\tif existing:\n'
'\t\t\treturn existing["name"]'
)
new = (
'\t\t\t{"user": user, "status": "Open", "docstatus": 1},\n'
'\t\t\t["name", "pos_profile"], as_dict=True,\n'
'\t\t)\n'
'\t\tif existing:\n'
'\t\t\treturn existing["name"]'
)
if old not in s:
    raise SystemExit("ANCHOR ensure_pos_opening_entry get_value NOT FOUND")
s = s.replace(old, new, 1)
open(p, "w", encoding="utf-8").write(s)
print("PATCHED ensure_pos_opening_entry get_value -> as_dict=True")
