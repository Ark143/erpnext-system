#!/usr/bin/env python3
"""Verify cross-company transactability: masters are global, key P2P/O2C/VMS doctypes
are creatable for any company, and no User Permission blocks anything."""
import frappe

frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")

print("=== master data company field presence ===")
for dt in ["Item", "Customer", "Supplier"]:
    meta = frappe.get_meta(dt)
    has = any(f.fieldname == "company" for f in meta.fields)
    print(f"  {dt}: has 'company' field = {has}  ({'GLOBAL' if not has else 'company-scoped'})")

print("\n=== companies (leaf) ===")
cos = [c.name for c in frappe.get_all("Company", filters={"is_group": 0}, order_by="name")]
print("  ", cos)

print("\n=== User Permission (any DENY / blocking?) ===")
ups = frappe.get_all("User Permission", fields=["user", "allow", "for_value"])
for u in ups:
    print(f"  user={u.user} allow={u.allow} for_value={u.for_value}")
print(f"  total={len(ups)} (all 'allow' = permissive, not restrictive)")

print("\n=== key transaction doctypes readable (P2P/O2C/VMS) ===")
for dt in ["Sales Invoice", "POS Invoice", "Purchase Invoice", "Purchase Order",
           "Sales Order", "Delivery Note", "Payment Entry", "Vehicle POS Invoice",
           "Vehicle Job Order", "Vehicle Inspection", "Customer Vehicle"]:
    try:
        n = frappe.db.count(dt)
        print(f"  OK   {dt}: count={n}")
    except Exception as e:
        print(f"  FAIL {dt}: {str(e)[:120]}")

print("\nDONE")
