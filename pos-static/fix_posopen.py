p = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/doctype/vehicle_pos_invoice/vehicle_pos_invoice.py"
s = open(p, encoding="utf-8").read()

old = ("""\tdef ensure_pos_opening_entry(self, company, pos_profile):
\t\t\"\"\"Create an open POS Opening Entry for the current user if none is open.\"\"\"
\t\topen_entry = frappe.db.get_value(
\t\t\t"POS Opening Entry",
\t\t\t{"pos_profile": pos_profile, "user": frappe.session.user, "status": "Open", "docstatus": 1},
\t\t\t"name",
\t\t)
\t\tif open_entry:
\t\t\treturn open_entry""")

new = ("""\tdef ensure_pos_opening_entry(self, company, pos_profile):
\t\t\"\"\"Reuse an already-open POS Opening Entry for the current user, else create one.
\t\tReusing ANY open entry for the user prevents Frappe's
\t\t"Cashier is currently assigned to another POS" validation when an open entry
\t\talready exists under a different POS Profile.\"\"\"
\t\topen_entry = frappe.db.get_value(
\t\t\t"POS Opening Entry",
\t\t\t{"user": frappe.session.user, "status": "Open", "docstatus": 1},
\t\t\t"name",
\t\t)
\t\tif open_entry:
\t\t\treturn open_entry""")

if old not in s:
    raise SystemExit("ANCHOR NOT FOUND")
if "Reuse an already-open POS Opening Entry" in s:
    print("ALREADY PATCHED")
else:
    s = s.replace(old, new, 1)
    open(p, "w", encoding="utf-8").write(s)
    print("PATCHED ensure_pos_opening_entry: reuse any open entry for user")
