p = "/workspace/frappe-bench/apps/erpnext/erpnext/accounts/doctype/pos_closing_entry/pos_closing_entry.py"
s = open(p, encoding="utf-8").read()

old = (
"\t\t\tgroupby(SalesInvoicePayment.mode_of_payment)\n"
"\t\t\t.select(\n"
"\t\t\t\tSalesInvoicePayment.mode_of_payment,\n"
"\t\t\t\tSalesInvoicePayment.account,\n"
)
new = (
"\t\t\tgroupby(SalesInvoicePayment.mode_of_payment, SalesInvoicePayment.account)\n"
"\t\t\t.select(\n"
"\t\t\t\tSalesInvoicePayment.mode_of_payment,\n"
"\t\t\t\tSalesInvoicePayment.account,\n"
)
if old not in s:
    raise SystemExit("ANCHOR get_payments NOT FOUND")
s = s.replace(old, new, 1)
open(p, "w", encoding="utf-8").write(s)
print("PATCHED get_payments GROUP BY to include account (PostgreSQL compat)")
