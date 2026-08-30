import frappe, json, sys
try:
    frappe.init(site="erp.localhost", sites_path="/workspace/frappe-bench/sites")
except Exception:
    frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect(); frappe.set_user("Administrator")
out = {}
for dt, names in [
    ("Web Page", ["vehicle-pos-terminal"]),
    ("Server Script", ["VM POS Items", "VM POS Meta", "VM POS Vehicles", "VM POS Vehicle Customer", "VM POS Cashier", "VM POS History"]),
    ("Cashier Profile", None),
]:
    if names is None:
        names = [d.name for d in frappe.get_all(dt, filters={}, limit_page_length=200)]
    out[dt] = [frappe.get_doc(dt, n).as_dict() for n in names]
sys.stdout.write(json.dumps(out, default=str))
