p = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/doctype/vehicle_pos_invoice/vehicle_pos_invoice.py"
s = open(p, encoding="utf-8").read()

old = ("""\tdef ensure_pos_opening_entry(self, company, pos_profile):
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
\t\t\treturn open_entry

\t\tcash = self.get_mode_of_payment("Cash", company)
\t\tentry = frappe.get_doc(
\t\t\t{
\t\t\t\t"doctype": "POS Opening Entry",
\t\t\t\t"company": company,
\t\t\t\t"pos_profile": pos_profile,
\t\t\t\t"user": frappe.session.user,
\t\t\t\t"posting_date": frappe.utils.nowdate(),
\t\t\t\t"period_start_date": frappe.utils.now_datetime(),
\t\t\t\t"balance_details": [{"mode_of_payment": cash, "opening_amount": 0}],
\t\t\t}
\t\t)
\t\tentry.insert()
\t\tentry.submit()
\t\treturn entry.name""")

new = ("""\tdef ensure_pos_opening_entry(self, company, pos_profile):
\t\t\"\"\"Ensure exactly ONE open POS Opening Entry for the current user, matching
\t\tpos_profile. Frappe blocks creating a 2nd open entry for the same user
\t\t("Cashier is currently assigned to another POS") and also requires an open
\t\tentry for the *specific* POS Profile when the POS Invoice validates
\t\t("No open POS Opening Entry found"). So: reuse the matching open entry if
\t\tpresent, otherwise close any other open entry for this user and create one
\t\tfor the target profile.\"\"\"
\t\tuser = frappe.session.user
\t\topen_entries = frappe.get_all(
\t\t\t"POS Opening Entry",
\t\t\t{"user": user, "status": "Open", "docstatus": 1},
\t\t\t["name", "pos_profile"],
\t\t)
\t\tfor e in open_entries:
\t\t\tif e.pos_profile == pos_profile:
\t\t\t\treturn e.name
\t\t\t# close the mismatched open entry so we can open the correct profile
\t\t\ttry:
\t\t\t\tfrappe.get_doc("POS Opening Entry", e.name).cancel()
\t\t\texcept Exception:
\t\t\t\tpass

\t\tcash = self.get_mode_of_payment("Cash", company)
\t\tentry = frappe.get_doc(
\t\t\t{
\t\t\t\t"doctype": "POS Opening Entry",
\t\t\t\t"company": company,
\t\t\t\t"pos_profile": pos_profile,
\t\t\t\t"user": user,
\t\t\t\t"posting_date": frappe.utils.nowdate(),
\t\t\t\t"period_start_date": frappe.utils.now_datetime(),
\t\t\t\t"balance_details": [{"mode_of_payment": cash, "opening_amount": 0}],
\t\t\t}
\t\t)
\t\tentry.insert()
\t\tentry.submit()
\t\treturn entry.name""")

if old not in s:
    raise SystemExit("ANCHOR NOT FOUND")
s = s.replace(old, new, 1)
open(p, "w", encoding="utf-8").write(s)
print("PATCHED ensure_pos_opening_entry (close mismatched + create correct profile)")
