import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
from frappe.desk.query_report import run
# Simulate a non-admin user with NO user-default company (the cashier scenario)
test_user = frappe.get_all("User", filters={"name":["like","cashier%"]}, pluck="name")
print("cashier users:", test_user)
# run as a user who has no company default
for u in (test_user or ["Administrator"]):
    frappe.set_user(u)
    # ensure no user default company to mimic the bug
    cur = frappe.defaults.get_user_default("Company", u)
    print(f"user={u} user_default_company={cur}")
    try:
        res = run("Sales Order Trends", filters={"period":"Monthly","based_on":"Item","company":"ULTRA MRF"})
        print(f"  Sales Order Trends RUN OK for {u}: rows=", len(res.get("result",[])) if isinstance(res,dict) else "n/a")
    except Exception as e:
        print(f"  Sales Order Trends ERR for {u}:", type(e).__name__, str(e)[:90])
    frappe.set_user("Administrator")
# Also verify fiscal year exists for ULTRA MRF
print("\nFiscal Years:", frappe.get_all("Fiscal Year", pluck="name"))
