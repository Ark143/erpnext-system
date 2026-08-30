import frappe, traceback, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
real_sql = frappe.db.sql
def patched(query, *a, **k):
    try:
        return real_sql(query, *a, **k)
    except Exception as e:
        print("FIRST SQL FAIL:\n", str(e)[:400])
        raise
frappe.db.sql = patched
from frappe.desk.query_report import run
name = "Purchase Register"
fl = {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}
try:
    res = run(name, filters=fl)
    print("OK rows=", len(res.get("result",[])))
except Exception as e:
    print("REPORT RAISED:", type(e).__name__, str(e)[:120])
