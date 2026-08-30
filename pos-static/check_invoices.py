import frappe, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()

# 1) Vehicle POS Invoice
vpi = frappe.get_all("Vehicle POS Invoice", fields=["name", "customer", "vehicle", "total_amount", "paid_amount", "status", "pos_invoice", "creation"])
print("=== Vehicle POS Invoice docs ===")
print(json.dumps(vpi, indent=1, default=str))

# 2) The linked Sales Invoice (Accounting)
si = frappe.get_all("Sales Invoice", filters={"name": ["like", "ACC-PSINV%"]}, fields=["name", "customer", "grand_total", "status", "creation"])
print("=== Sales Invoice (ACC-PSINV) docs ===")
print(json.dumps(si, indent=1, default=str))

# 3) What does the POS get_history return for the current user?
import vehicle_management.vehicle_management.pos_api as pa
res = pa.get_history()
print("=== get_history() sample ===")
print(json.dumps(res[:1], indent=1, default=str)[:600])

# 4) Confirm doctype list routes exist
for dt in ["Vehicle POS Invoice", "Sales Invoice"]:
    print(f"Doctype '{dt}' exists:", frappe.db.exists("DocType", dt))
