import frappe, json, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()

# 1) Fiscal Year check
fys = frappe.get_all("Fiscal Year", fields=["name","year_start_date","year_end_date"])
print("Fiscal Years:", fys)
companies = frappe.get_all("Company", fields=["name"])
print("Companies:", companies)

# 2) General Ledger full traceback
from frappe.desk.query_report import run
try:
    res = run("General Ledger", filters={"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31","account":"%"})
    print("GL OK rows:", len(res.get("result",[])))
except Exception:
    print("GL TRACEBACK:")
    print(traceback.format_exc()[-2500:])
