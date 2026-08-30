import frappe, sys, io, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
import erpnext.selling.report.sales_order_trends.sales_order_trends as sot
# Build filters exactly like the chart: period, based_on, company
filters = frappe._dict({"period":"Monthly","based_on":"Item","company":"ULTRA MRF","fiscal_year":frappe.defaults.get_global_default("fiscal_year")})
# Run the report's own execute, capture first error
buf=io.StringIO()
try:
    old=sys.stdout; sys.stdout=buf
    res = sot.execute(filters)
    sys.stdout=old
    print("REPORT OK -> result type:", type(res), "| rows:", len(res[0]) if isinstance(res,tuple) and res else "n/a")
except Exception as e:
    sys.stdout=sys.__stdout__
    print("FIRST REPORT ERROR:", type(e).__name__, str(e)[:200])
    # get the underlying SQL error if wrapped
    print("--- traceback tail ---")
    traceback.print_exc(limit=4)
print(buf.getvalue()[:500])
