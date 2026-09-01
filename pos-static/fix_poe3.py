p = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/doctype/vehicle_pos_invoice/vehicle_pos_invoice.py"
s = open(p, encoding="utf-8").read()

# fix: get_value with list returns tuple; use as_dict=True
s = s.replace(
    '{"user": frappe.session.user, "status": "Open", "docstatus": 1},\n\t\t\t["name", "pos_profile"],\n\t\t)',
    '{"user": frappe.session.user, "status": "Open", "docstatus": 1},\n\t\t\t["name", "pos_profile"], as_dict=True,\n\t\t)')
s = s.replace(
    '{"user": frappe.session.user, "status": "Open", "docstatus": 1},\n\t\t\t["pos_profile", "company"],\n\t\t)',
    '{"user": frappe.session.user, "status": "Open", "docstatus": 1},\n\t\t\t["pos_profile", "company"], as_dict=True,\n\t\t)')

if 'as_dict=True' not in s:
    raise SystemExit("patch did not apply")
open(p, "w", encoding="utf-8").write(s)
print("PATCHED: get_value -> as_dict=True in ensure_pos_opening_entry + create_erpnext_pos_invoice")
