p = "/workspace/frappe-bench/apps/erpnext/erpnext/accounts/doctype/pos_closing_entry/pos_closing_entry.py"
s = open(p, encoding="utf-8").read()

old = "fn.Timestamp(InvoiceDocType.posting_date, InvoiceDocType.posting_time)"
new = "fn.CombineDatetime(InvoiceDocType.posting_date, InvoiceDocType.posting_time)"
count = s.count(old)
if count == 0:
    raise SystemExit("ANCHOR NOT FOUND")
s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)
print(f"PATCHED {count} occurrences of fn.Timestamp -> fn.CombineDatetime in pos_closing_entry.py")
