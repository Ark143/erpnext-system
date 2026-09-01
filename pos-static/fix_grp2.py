import re
p = "/workspace/frappe-bench/apps/erpnext/erpnext/accounts/doctype/pos_closing_entry/pos_closing_entry.py"
s = open(p, encoding="utf-8").read()

# Only the get_payments groupby references SalesInvoicePayment.mode_of_payment
pat = r"groupby\(SalesInvoicePayment\.mode_of_payment\)"
if not re.search(pat, s):
    raise SystemExit("pattern not found")
# Ensure we don't double-add account
if "groupby(SalesInvoicePayment.mode_of_payment, SalesInvoicePayment.account)" in s:
    print("ALREADY PATCHED")
else:
    s = re.sub(pat, "groupby(SalesInvoicePayment.mode_of_payment, SalesInvoicePayment.account)", s, count=1)
    open(p, "w", encoding="utf-8").write(s)
    print("PATCHED get_payments GROUP BY to include account")
