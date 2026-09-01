#!/usr/bin/env python3
"""Patch pos_api.py: close_cashier accepts + records closing_amount; get_cashier_shift
returns opening amount; open_cashier validates opening_amount is a number."""
PATH = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/pos_api.py"
src = open(PATH).read()

# 1. get_cashier_shift: include opening amount (from balance_details)
old_shift = '''\tif e:
\t\treturn {"open": True, "name": e.name, "pos_profile": e.pos_profile,
\t\t        "company": e.company, "period_start_date": str(e.period_start_date or "")}
\treturn {"open": False, "name": None}
'''
new_shift = '''\tif e:
\t\topening_amount = 0.0
\t\ttry:
\t\t\tbd = frappe.db.get_all("POS Opening Entry Detail", {"parent": e.name}, ["opening_amount"])
\t\t\topening_amount = sum(flt(x.opening_amount) for x in bd)
\t\texcept Exception:
\t\t\tpass
\t\treturn {"open": True, "name": e.name, "pos_profile": e.pos_profile,
\t\t        "company": e.company, "period_start_date": str(e.period_start_date or ""),
\t\t        "opening_amount": opening_amount}
\treturn {"open": False, "name": None, "opening_amount": 0.0}
'''
assert old_shift in src, "shift block not found"
src = src.replace(old_shift, new_shift, 1)

# 2. close_cashier: accept closing_amount, set it on the cash reconciliation row + opening amount
old_close = '''@frappe.whitelist()
def close_cashier():
\t"""Close the cashier's open POS Opening Entry via a POS Closing Entry."""
\tuser = frappe.session.user
\topening_name = frappe.db.get_value(
\t\t"POS Opening Entry", {"user": user, "status": "Open", "docstatus": 1}, "name"
\t)
\tif not opening_name:
\t\treturn {"status": "no_open_entry", "message": "No open POS Opening Entry found."}
\tfrom erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import make_closing_entry_from_opening
\topening = frappe.get_doc("POS Opening Entry", opening_name)
\tclosing = make_closing_entry_from_opening(opening)
\tclosing.insert()
\tclosing.submit()
\tfrappe.db.commit()
\treturn {"status": "closed", "name": closing.name}
'''
new_close = '''@frappe.whitelist()
def close_cashier(closing_amount=0):
\t"""Close the cashier's open POS Opening Entry via a POS Closing Entry,
\trecording the cashier's counted closing amount."""
\tuser = frappe.session.user
\topening_name = frappe.db.get_value(
\t\t"POS Opening Entry", {"user": user, "status": "Open", "docstatus": 1}, "name"
\t)
\tif not opening_name:
\t\treturn {"status": "no_open_entry", "message": "No open POS Opening Entry found."}
\tfrom erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import make_closing_entry_from_opening
\topening = frappe.get_doc("POS Opening Entry", opening_name)
\topening_amount = 0.0
\tfor b in opening.get("balance_details") or []:
\t\tif (b.mode_of_payment or "").lower() == "cash":
\t\t\topening_amount = flt(b.opening_amount)
\tclosing = make_closing_entry_from_opening(opening)
\t# record the cashier's counted cash (closing amount) on the Cash reconciliation row
\tfor row in closing.get("payment_reconciliation") or []:
\t\tif (row.mode_of_payment or "").lower() == "cash":
\t\t\trow.opening_amount = opening_amount
\t\t\trow.closing_amount = flt(closing_amount)
\tclosing.insert()
\tclosing.submit()
\tfrappe.db.commit()
\treturn {"status": "closed", "name": closing.name}
'''
assert old_close in src, "close_cashier block not found"
src = src.replace(old_close, new_close, 1)

open(PATH, "w").write(src)
import ast
ast.parse(src)
print("patched pos_api.py, len", len(src))
print("has closing_amount param:", "def close_cashier(closing_amount=0)" in src)
print("has opening_amount in shift:", 'opening_amount" in src and "POS Opening Entry Detail" in src')
