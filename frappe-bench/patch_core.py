import re

# ---- Fix A: get_closing_entry_for_closed_period (Postgres rejects ORDER BY creation on aggregate) ----
pA = '/workspace/frappe-bench/apps/erpnext/erpnext/stock/doctype/stock_closing_entry/stock_closing_entry.py'
sA = open(pA).read()
mA = re.search(r'([ \t]*)frappe\.db\.get_value\(\s*"Period Closing Voucher",\s*\{"docstatus": 1, "company": company\},\s*\[\{"MAX": "period_end_date"\}\]\s*\)', sA, re.DOTALL)
assert mA, "Fix A anchor not found"
ind = mA.group(1)
newA = (ind + 'frappe.db.sql(\n' + ind + '\t\'SELECT MAX(period_end_date) FROM "tabPeriod Closing Voucher" WHERE docstatus=1 AND company=%s\',\n'
        + ind + '\tcompany,\n' + ind + '\tas_scalar=True,\n' + ind + ')')
sA = sA[:mA.start()] + newA + sA[mA.end():]
open(pA, 'w').write(sA)
print("Fix A applied")

# ---- Fix B: set_landed_cost_voucher_amount missing GROUP BY ----
pB = '/workspace/frappe-bench/apps/erpnext/erpnext/controllers/stock_controller.py'
sB = open(pB).read()
mB = re.search(r'([ \t]*)\.where\(\(lcv_item\.docstatus == 1\) & \(lcv_item\.receipt_document == self\.name\)\)', sB)
assert mB, "Fix B anchor not found"
indB = mB.group(1)
sB = sB[:mB.end()] + '\n' + indB + '\t.groupby(lcv_item.cost_center)' + sB[mB.end():]
open(pB, 'w').write(sB)
print("Fix B applied")

# ---- Instrument generator to print full tracebacks on error ----
pG = '/workspace/frappe-bench/generate_run.py'
sG = open(pG).read()
sG = sG.replace('import frappe\n', 'import frappe\nimport traceback\n', 1)
sG = sG.replace('print(f"  ! O2C Error in {company}: {e}")', 'traceback.print_exc(); print(f"  ! O2C Error in {company}: {e}")')
sG = sG.replace('print(f"  ! P2P Error in {company}: {e}")', 'traceback.print_exc(); print(f"  ! P2P Error in {company}: {e}")')
sG = sG.replace('print(f"  ! Stock Entry Error in {company}: {e}")', 'traceback.print_exc(); print(f"  ! Stock Entry Error in {company}: {e}")')
open(pG, 'w').write(sG)
print("Generator instrumented")
