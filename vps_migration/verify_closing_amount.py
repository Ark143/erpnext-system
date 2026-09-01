#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
c = frappe.get_doc("POS Closing Entry", "POS-CLO-2026-00004")
print("closing entry:", c.name, "status", c.status)
for r in c.get("payment_reconciliation") or []:
    print(f"  {r.mode_of_payment}: opening={r.opening_amount} expected={r.expected_amount} closing={r.closing_amount} diff={r.difference}")
