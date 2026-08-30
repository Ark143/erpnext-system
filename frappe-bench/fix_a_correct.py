import re
p = '/workspace/frappe-bench/apps/erpnext/erpnext/stock/doctype/stock_closing_entry/stock_closing_entry.py'
s = open(p).read()
m = re.search(
    r'([ \t]*)closed_upto = frappe\.db\.sql\(\s*'
    r"'SELECT MAX\(period_end_date\) FROM \"tabPeriod Closing Voucher\" WHERE docstatus=1 AND company=%s',\s*"
    r'company,\s*as_scalar=True,\s*\)',
    s,
)
assert m, "anchor not found"
ind = m.group(1)
new = (
    ind + 'res = frappe.db.sql(\n'
    + ind + '\t\'SELECT MAX(period_end_date) FROM "tabPeriod Closing Voucher" WHERE docstatus=1 AND company=%s\',\n'
    + ind + '\tcompany,\n'
    + ind + '\tas_list=True,\n'
    + ind + ')\n'
    + ind + 'closed_upto = res[0][0] if res else None'
)
s = s[:m.start()] + new + s[m.end():]
open(p, 'w').write(s)
print("Fix A corrected")
