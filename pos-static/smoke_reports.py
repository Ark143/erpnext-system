import frappe, sys, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
from frappe.desk.query_report import run

# Reports touched by the loop (runtime-critical script reports).
# Each run in a subprocess in real use; here we run sequentially with rollback safety.
reports = [
    ("Sales Order Trends", {"period":"Monthly","based_on":"Item","company":"ULTRA MRF"}),
    ("Purchase Order Trends", {"period":"Monthly","based_on":"Item","company":"ULTRA MRF","period_based_on":"posting_date"}),
    ("Delivery Note Trends", {"period":"Yearly","based_on":"Customer","company":"ULTRA MRF"}),
    ("Purchase Receipt Trends", {"period":"Monthly","based_on":"Supplier","company":"ULTRA MRF","period_based_on":"posting_date"}),
    ("Sales Analytics", {"based_on":"Item","company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ("Sales Register", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ("Purchase Register", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ("Cash Flow", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31","periodicity":"Monthly"}),
    ("Gross Profit", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ("Accounts Receivable", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ("Stock Ledger", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ("Batch Wise Balance History", {"item_code":None,"company":"ULTRA MRF"}),
]
ok=0; fail=0
for name, fl in reports:
    try:
        frappe.db.rollback()
        res = run(name, filters=fl)
        n = len(res.get("result",[])) if isinstance(res, dict) else 0
        print(f"OK   {name}: rows={n}")
        ok+=1
    except Exception as e:
        print(f"FAIL {name}: {type(e).__name__}: {str(e)[:120]}")
        fail+=1
print(f"\nSUMMARY: ok={ok} fail={fail}")
