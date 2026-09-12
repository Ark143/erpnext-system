import os

def patch_file(F, replacements):
    bak = F + ".bak_pre_patch"
    if not os.path.exists(bak):
        open(bak, "w", encoding="utf-8").write(open(F, encoding="utf-8").read())
    s = open(F, encoding="utf-8").read()
    for old, new in replacements:
        assert old in s, f"ANCHOR NOT FOUND in {F}:\n{old!r}"
        s = s.replace(old, new, 1)
    open(F, "w", encoding="utf-8").write(s)
    print(f"PATCHED {F}")

# ---- erpnext/accounts/utils.py ----
utils = "/workspace/frappe-bench/apps/erpnext/erpnext/accounts/utils.py"
patch_file(utils, [
    # Bug 1: query_voucher_amount GROUP BY missing non-aggregate selected cols
    (
        "\t\t\t.groupby(ple.voucher_type, ple.voucher_no, ple.party_type, ple.party)\n",
        "\t\t\t.groupby(ple.account, ple.voucher_type, ple.voucher_no, ple.party_type, ple.party, ple.posting_date, ple.due_date, ple.account_currency, ple.cost_center, ple.remarks)\n",
    ),
    # Bug 3: unqualified qb.Field in subquery HAVING leaks onto outer CTE (PG HAVING alias err)
    (
        '\t\t\t.having(qb.Field("amount_in_account_currency") > 0)\n',
        '\t\t\t.having(ple.amount_in_account_currency > 0)\n',
    ),
])

# ---- erpnext/accounts/general_ledger.py ----
gl = "/workspace/frappe-bench/apps/erpnext/erpnext/accounts/general_ledger.py"
patch_file(gl, [
    (
        '\tlast_pcv_date = frappe.db.get_value(\n'
        '\t\t"Period Closing Voucher", {"docstatus": 1, "company": company}, [{"MAX": "period_end_date"}]\n'
        '\t)\n',
        '\tlast_pcv_date = frappe.db.get_value(\n'
        '\t\t"Period Closing Voucher", {"docstatus": 1, "company": company}, "period_end_date", order_by="period_end_date desc"\n'
        '\t)\n',
    ),
])
# ---- erpnext/accounts/doctype/bank_reconciliation_tool/bank_reconciliation_tool.py ----
recon = "/workspace/frappe-bench/apps/erpnext/erpnext/accounts/doctype/bank_reconciliation_tool/bank_reconciliation_tool.py"
patch_file(recon, [
    (
        "\t\t.groupby(je.name)\n",
        "\t\t.groupby(je.name, je.cheque_no, je.cheque_date, je.pay_to_recd_from, jea.party_type, je.posting_date, jea.account_currency)\n",
    ),
])

# ---- erpnext/accounts/doctype/bank_clearance/bank_clearance.py ----
clearance = "/workspace/frappe-bench/apps/erpnext/erpnext/accounts/doctype/bank_clearance/bank_clearance.py"
patch_file(clearance, [
    (
        "\tjournal_entries = (\n\t\tjournal_entry_query.groupby(journal_entry_account.account, journal_entry.name)\n",
        "\tjournal_entries = (\n\t\tjournal_entry_query.groupby(journal_entry_account.account, journal_entry.name, journal_entry.cheque_no, journal_entry.cheque_date, journal_entry.posting_date, journal_entry_account.against_account, journal_entry.clearance_date, journal_entry_account.account_currency)\n",
    ),
])

# ---- erpnext/stock/stock_balance.py ----
stock_bal = "/workspace/frappe-bench/apps/erpnext/erpnext/stock/stock_balance.py"
patch_file(stock_bal, [
    (
        "case when dont_reserve_qty_for_stock_items then",
        "case when dont_reserve_qty_for_stock_items = 1 then",
    ),
    (
        "case when dont_reserve_qty_on_return then",
        "case when dont_reserve_qty_on_return = 1 then",
    ),
])

print("ALL PATCHES APPLIED")
