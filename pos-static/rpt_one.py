import frappe, sys, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
from frappe.desk.query_report import run
name = sys.argv[1]
fl = json.loads(sys.argv[2])
try:
    res = run(name, filters=fl)
    print("OK rows=" + str(len(res.get("result", [])) if isinstance(res, dict) else 0))
except Exception as e:
    print("FAIL " + type(e).__name__ + ": " + str(e)[:160])
