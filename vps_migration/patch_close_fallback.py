#!/usr/bin/env python3
"""Fix close_cashier: ensure a Cash reconciliation row exists even with zero sales,
so the cashier's closing amount is always recorded."""
PATH = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/pos_api.py"
src = open(PATH).read()

old = '''\tclosing = make_closing_entry_from_opening(opening)
\t# record the cashier's counted cash (closing amount) on the Cash reconciliation row
\tfor row in closing.get("payment_reconciliation") or []:
\t\tif (row.mode_of_payment or "").lower() == "cash":
\t\t\trow.opening_amount = opening_amount
\t\t\trow.closing_amount = flt(closing_amount)
\tclosing.insert()
\tclosing.submit()
'''
new = '''\tclosing = make_closing_entry_from_opening(opening)
\t# record the cashier's counted cash (closing amount) on the Cash reconciliation row.
\t# If there were no sales in the shift, make_closing_entry_from_opening leaves
\t# payment_reconciliation empty — ensure a Cash row exists so the amount is recorded.
\trows = closing.get("payment_reconciliation") or []
\tcash_rows = [r for r in rows if (r.get("mode_of_payment") or "").lower() == "cash"]
\tif cash_rows:
\t\tfor r in cash_rows:
\t\t\tr.opening_amount = opening_amount
\t\t\tr.closing_amount = flt(closing_amount)
\telse:
\t\tclosing.append("payment_reconciliation", {
\t\t\t"mode_of_payment": opening.get("balance_details")[0].mode_of_payment if opening.get("balance_details") else "Cash",
\t\t\t"opening_amount": opening_amount,
\t\t\t"expected_amount": 0,
\t\t\t"closing_amount": flt(closing_amount),
\t\t})
\tclosing.insert()
\tclosing.submit()
'''
assert old in src, "close block not found"
src = src.replace(old, new, 1)

open(PATH, "w").write(src)
import ast
ast.parse(src)
print("patched. len", len(src))
print("has append fallback:", 'closing.append("payment_reconciliation"' in src)
