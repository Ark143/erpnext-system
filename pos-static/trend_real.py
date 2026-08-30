import frappe, sys, io, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
from frappe.desk.query_report import run
# force a rollback to clear any poisoned state
frappe.db.rollback()
frappe.set_user("cashier.test@example.com")
buf=io.StringIO(); sys.stdout=buf
try:
    res = run("Sales Order Trends", filters={"period":"Monthly","based_on":"Item","company":"ULTRA MRF"})
    print("RESULT OK rows:", len(res.get("result",[])) if isinstance(res,dict) else "n/a")
except Exception as e:
    print("FIRST ERROR:", type(e).__name__)
    print(str(e)[:300])
    print("--- traceback (top) ---")
    traceback.print_exc(limit=6)
sys.stdout=sys.__stdout__
print(buf.getvalue())
