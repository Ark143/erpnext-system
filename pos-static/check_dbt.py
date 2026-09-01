import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
print("frappe.conf.db_type:", repr(frappe.conf.db_type))
print("frappe.db.db_type:", repr(frappe.db.db_type))
from frappe.query_builder import DocType
from frappe.query_builder.functions import CombineDatetime
si = DocType("Sales Invoice")
q = frappe.qb.from_(si).select(CombineDatetime(si.posting_date, si.posting_time))
print("CombineDatetime SQL:", q.get_sql())
# also raw timestamp via functions
from frappe.query_builder.functions import Timestamp
try:
    print("Timestamp SQL:", Timestamp(si.posting_date, si.posting_time).get_sql())
except Exception as e:
    print("Timestamp err:", e)
