import frappe, sys, io, traceback, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
from frappe.desk.query_report import run
for name, fl in [("Purchase Register", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
                ("Sales Analytics", {"based_on":"Item","company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31","range":"age"}),
                ("Gross Profit", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"})]:
    try:
        res = run(name, filters=fl)
        print(f"{name}: OK rows={len(res.get('result',[]))}")
    except Exception as e:
        print(f"\n=== {name} ERROR ===")
        print(traceback.format_exc().split("The above exception")[0][-1500:])
