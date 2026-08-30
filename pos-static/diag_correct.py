import frappe, traceback, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
from frappe.desk.query_report import run
tests = [
    ("Sales Analytics", {"doc_type":"Sales Invoice","based_on":"Item","company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31","range":"age","value_quantity":"Value"}),
    ("Gross Profit", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31","group_by":"Invoice"}),
    ("Cash Flow", {"company":"ULTRA MRF","period_start_date":"2026-01-01","period_end_date":"2026-12-31","periodicity":"Monthly"}),
]
for name, fl in tests:
    try:
        res = run(name, filters=fl)
        print(f"OK {name}: rows={len(res.get('result',[]))}")
    except Exception as e:
        print(f"REPORT RAISED {name}: {type(e).__name__}: {str(e)[:160]}")
