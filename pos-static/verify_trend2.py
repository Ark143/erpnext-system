import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
from frappe.desk.query_report import run
u = frappe.get_all("User", filters={"name":["like","cashier%"]}, pluck="name")
print("cashier users:", u)
who = u[0] if u else "Administrator"
frappe.set_user(who)
print(f"running Sales Order Trends as {who} (user_default_company={frappe.defaults.get_user_default('Company', who)})")
try:
    res = run("Sales Order Trends", filters={"period":"Monthly","based_on":"Item","company":"ULTRA MRF"})
    print("RESULT OK -> keys:", list(res.keys()) if isinstance(res,dict) else type(res), "| result rows:", len(res.get("result",[])) if isinstance(res,dict) else "n/a")
except Exception as e:
    import traceback; traceback.print_exc()
    print("ERR:", type(e).__name__, str(e)[:120])
