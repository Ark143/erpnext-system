import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
from frappe.desk.query_report import run
tests = [
    ("Sales Order Trends", {"period":"Monthly","based_on":"Item","company":"ULTRA MRF"}),
    ("Purchase Order Trends", {"period":"Monthly","based_on":"Item","company":"ULTRA MRF","period_based_on":"posting_date"}),
    ("Delivery Note Trends", {"period":"Yearly","based_on":"Customer","company":"ULTRA MRF"}),
    ("Purchase Receipt Trends", {"period":"Monthly","based_on":"Supplier","company":"ULTRA MRF","period_based_on":"posting_date"}),
]
for name, fl in tests:
    try:
        res = run(name, filters=fl)
        n = len(res.get("result",[])) if isinstance(res,dict) else "n/a"
        print(f"OK  {name}: rows={n}")
    except Exception as e:
        print(f"ERR {name}: {type(e).__name__}: {str(e)[:90]}")
