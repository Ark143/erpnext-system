p = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/doctype/vehicle_pos_invoice/vehicle_pos_invoice.py"
s = open(p, encoding="utf-8").read()

# 1) ensure_pos_opening_entry: reuse any open entry for the user (no cancel)
old1 = ("""\tdef ensure_pos_opening_entry(self, company, pos_profile):
\t\t\"\"\"Ensure exactly ONE open POS Opening Entry for the current user.
\t\tFrappe blocks a 2nd open entry for the same user
\t\t("Cashier is currently assigned to another POS") and the POS Invoice
\t\tvalidation requires an open entry for the *specific* POS Profile
\t\t("No open POS Opening Entry found"). So: cancel EVERY open entry for this
\t\tuser (commit), then create exactly one open entry for the target profile.\"\"\"
\t\tuser = frappe.session.user
\t\tcash = self.get_mode_of_payment("Cash", company)

\t\topen_entries = frappe.get_all(
\t\t\t"POS Opening Entry",
\t\t\t{"user": user, "status": "Open", "docstatus": 1},
\t\t\t["name"],
\t\t)
\t\tfor e in open_entries:
\t\t\ttry:
\t\t\t\tfrappe.get_doc("POS Opening Entry", e.name).cancel()
\t\t\texcept Exception:
\t\t\t\tpass
\t\tfrappe.db.commit()

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
\t\tfrappe.db.commit()
\t\treturn entry.name""")

new1 = ("""\tdef ensure_pos_opening_entry(self, company, pos_profile):
\t\t\"\"\"Reuse an already-open POS Opening Entry for the current user, else create one.
\t\tFrappe blocks a 2nd open entry for the same user
\t\t("Cashier is currently assigned to another POS") and the POS Invoice
\t\tvalidation requires an open entry for the *specific* POS Profile
\t\t("No open POS Opening Entry found"). We therefore REUSE any open entry for
\t\tthis user (do NOT cancel it -- cancelling can be blocked by unconsolidated
\t\tinvoices). The matching pos_profile/company is taken from that open entry
\t\tby the caller so the POS Invoice validation stays consistent.\"\"\"
\t\tuser = frappe.session.user
\t\texisting = frappe.get_value(
\t\t\t"POS Opening Entry",
\t\t\t{"user": user, "status": "Open", "docstatus": 1},
\t\t\t["name", "pos_profile"],
\t\t)
\t\tif existing:
\t\t\treturn existing["name"]

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
\t\tfrappe.db.commit()
\t\treturn entry.name""")

if old1 not in s:
    raise SystemExit("ANCHOR ensure_pos_opening_entry NOT FOUND")
s = s.replace(old1, new1, 1)

# 2) create_erpnext_pos_invoice: derive pos_profile/company from the open entry
old2 = ("""\t\tcompany = self.company or frappe.defaults.get_user_default("Company")
\t\tpos_profile = self.ensure_pos_profile(company)
\t\tself.ensure_pos_opening_entry(company, pos_profile)""")
new2 = ("""\t\tcompany = self.company or frappe.defaults.get_user_default("Company")
\t\t# Reuse an already-open POS Opening Entry for this user (its profile/company
\t\t# must match the POS Invoice we are about to create).
\t\texisting = frappe.get_value(
\t\t\t"POS Opening Entry",
\t\t\t{"user": frappe.session.user, "status": "Open", "docstatus": 1},
\t\t\t["pos_profile", "company"],
\t\t)
\t\tif existing:
\t\t\tpos_profile = existing["pos_profile"]
\t\t\tif existing["company"]:
\t\t\t\tcompany = existing["company"]
\t\telse:
\t\t\tpos_profile = self.ensure_pos_profile(company)
\t\tself.ensure_pos_opening_entry(company, pos_profile)""")

if old2 not in s:
    raise SystemExit("ANCHOR create_erpnext_pos_invoice NOT FOUND")
s = s.replace(old2, new2, 1)

open(p, "w", encoding="utf-8").write(s)
print("PATCHED: ensure_pos_opening_entry (reuse) + create_erpnext_pos_invoice (derive profile from open entry)")
