import frappe, json, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
from frappe.desk.query_report import run

print("=== Reports with PROPER inputs ===")
for rpt, filt in [
    ("General Ledger", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ("Trial Balance", {"company":"ULTRA MRF","fiscal_year":"2026"}),
    ("Stock Ledger", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ("Accounts Receivable", {"company":"ULTRA MRF","report_date":"2026-12-31"}),
]:
    try:
        res = run(rpt, filters=filt)
        print(f"  {rpt:20} OK rows={len(res.get('result',[]))}")
    except Exception as e:
        print(f"  {rpt:20} FAIL {type(e).__name__}: {str(e)[:120]}")

print("\n=== Transaction creation (real module test) ===")
# minimal Sales Order
try:
    cust = frappe.get_all("Customer", filters={"customer_name":"JOAN CHIIETE"}, pluck="name")
    item = frappe.get_all("Item", filters={"is_sales_item":1,"disabled":0}, limit=1, pluck="name")
    wh = frappe.get_all("Warehouse", filters={"company":"ULTRA MRF"}, limit=1, pluck="name")
    print("  found cust=%s item=%s wh=%s" % (cust, item, wh))
    if cust and item and wh:
        so = frappe.get_doc({
            "doctype":"Sales Order","customer":cust[0],"company":"ULTRA MRF",
            "delivery_date":"2026-12-31",
            "items":[{"item_code":item[0],"qty":1,"rate":100,"warehouse":wh[0]}]
        })
        so.insert(ignore_permissions=True)
        print("  Sales Order created:", so.name)
        frappe.delete_doc("Sales Order", so.name, ignore_permissions=True, force=True)
        print("  (test Sales Order deleted)")
except Exception:
    print("  Sales Order FAIL:")
    print(traceback.format_exc()[-1500:])
