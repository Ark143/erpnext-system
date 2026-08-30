p = '/workspace/frappe-bench/apps/erpnext/erpnext/accounts/utils.py'
s = open(p).read()

old1 = '.groupby(ple.voucher_type, ple.voucher_no, ple.party_type, ple.party)'
new1 = '.groupby(ple.account, ple.voucher_type, ple.voucher_no, ple.party_type, ple.party, ple.posting_date, ple.due_date, ple.cost_center, ple.remarks)'
assert s.count(old1) == 1, "expected exactly 1 of groupby1, found %d" % s.count(old1)
s = s.replace(old1, new1)

old2 = '.groupby(ple.against_voucher_type, ple.against_voucher_no, ple.party_type, ple.party)'
new2 = '.groupby(ple.account, ple.against_voucher_type, ple.against_voucher_no, ple.party_type, ple.party, ple.posting_date, ple.due_date, ple.account_currency)'
assert s.count(old2) == 1, "expected exactly 1 of groupby2, found %d" % s.count(old2)
s = s.replace(old2, new2)

open(p, 'w').write(s)
print("Fix C applied")
