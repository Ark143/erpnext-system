import sys, os
sys.path.insert(0, '/workspace/frappe-bench/apps/frappe')
sys.path.insert(0, '/workspace/frappe-bench/apps/erpnext')
sys.path.insert(0, '/workspace/frappe-bench/apps/vehicle_management')
import frappe
os.chdir('/workspace/frappe-bench/sites')
frappe.init('site1.local'); frappe.connect()
from erpnext.accounts.utils import QueryPaymentLedger
q = QueryPaymentLedger()
q.reset()
q.vouchers = [frappe._dict({"voucher_type":"Sales Invoice","voucher_no":"X"})]
q.common_filter = []
q.query_for_outstanding()
try:
    sql = q.cte_query_voucher_amount_and_outstanding.get_sql()
    print("SQL_START")
    print(sql)
    print("SQL_END")
except Exception as e:
    print("GETSQL_ERR", repr(e))
    try:
        q.cte_query_voucher_amount_and_outstanding.run()
    except Exception as e2:
        print("RUN_ERR", str(e2)[:2000])
frappe.db.close()
