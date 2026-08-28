import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
os.chdir('sites')
import frappe
from frappe.query_builder import DocType
from pypika import CustomFunction

frappe.init(site='erp.localhost')
frappe.connect()

InvoiceDocType = DocType("Sales Invoice")
# Test various expressions on PostgreSQL
try:
    ts_expr = InvoiceDocType.posting_date + InvoiceDocType.posting_time
    q = frappe.qb.from_(InvoiceDocType).select(InvoiceDocType.name, ts_expr.as_("timestamp")).limit(1)
    res = q.run(as_dict=1)
    print("Test 1 (posting_date + posting_time) SUCCESS:", res)
except Exception as e:
    print("Test 1 FAILED:", e)

try:
    # Test concat custom function
    ConcatWS = CustomFunction("concat_ws", ["separator", "arg1", "arg2"])
    ts_expr2 = ConcatWS(" ", InvoiceDocType.posting_date, InvoiceDocType.posting_time)
    q2 = frappe.qb.from_(InvoiceDocType).select(InvoiceDocType.name, ts_expr2.as_("timestamp")).limit(1)
    res2 = q2.run(as_dict=1)
    print("Test 2 (concat_ws) SUCCESS:", res2)
except Exception as e:
    print("Test 2 FAILED:", e)
