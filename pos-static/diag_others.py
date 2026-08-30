import frappe, traceback, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
real_sql = frappe.db.sql
def patched(query, *a, **k):
    try: return real_sql(query, *a, **k)
    except Exception as e:
        print("FIRST SQL FAIL:", str(e)[:300]); raise
frappe.db.sql = patched
from frappe.desk.query_report import run
tests = [
    ("Sales Analytics", {"based_on":"Item","company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31","range":"age"}),
    ("Gross Profit", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ("Cash Flow", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31","periodicity":"Monthly"}),
]
for name, fl in tests:
    try:
        res = run(name, filters=fl)
        print(f"OK {name}: rows={len(res.get('result',[]))}")
    except Exception as e:
        print(f"REPORT RAISED {name}: {type(e).__name__}: {str(e)[:140]}")
