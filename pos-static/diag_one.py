import frappe, sys, traceback, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
from frappe.desk.query_report import run
name = sys.argv[1]
fl = json.loads(sys.argv[2])
try:
    res = run(name, filters=fl)
    print(f"{name}: OK rows={len(res.get('result',[]))}")
except Exception as e:
    tb = traceback.format_exc()
    print(f"=== {name} ERROR ===")
    print(tb[:2200])
