#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
rows = frappe.db.get_all("POS Closing Entry Detail", {"parent": "POS-CLO-2026-00005"},
                         ["mode_of_payment", "opening_amount", "expected_amount", "closing_amount", "difference"])
print("POS-CLO-2026-00005 reconciliation rows:")
for r in rows:
    print(f"  {r.mode_of_payment}: opening={r.opening_amount} expected={r.expected_amount} closing={r.closing_amount} diff={r.difference}")
if not rows:
    print("  (empty)")
