#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
c = frappe.get_doc("POS Closing Entry", "POS-CLO-2026-00004")
print("payment_reconciliation raw:", c.get("payment_reconciliation"))
print("len:", len(c.get("payment_reconciliation") or []))
# also query the child table directly
rows = frappe.db.get_all("POS Closing Entry Detail", {"parent": "POS-CLO-2026-00004"},
                         ["mode_of_payment", "opening_amount", "expected_amount", "closing_amount", "difference"])
print("child rows:", rows)
