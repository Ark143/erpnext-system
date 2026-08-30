p = '/workspace/frappe-bench/apps/erpnext/erpnext/accounts/utils.py'
s = open(p).read()
old2 = '.groupby(ple.against_voucher_type, ple.against_voucher_no, ple.party_type, ple.party)'
new2 = '.groupby(ple.account, ple.against_voucher_type, ple.against_voucher_no, ple.party_type, ple.party, ple.posting_date, ple.due_date, ple.account_currency)'
n = s.count(old2)
assert n >= 1, "groupby2 not found"
s = s.replace(old2, new2)
open(p, 'w').write(s)
print("Fix C2 applied to %d occurrence(s)" % n)
