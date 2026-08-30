import frappe, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
frappe.session.user = "Administrator"
try:
    res = frappe.call("vm_company_dashboard_api", company="ULTRA MRF", period="this_year")
    print("OK:", type(res), str(res)[:120])
except Exception as e:
    tb = traceback.format_exc()
    for line in tb.splitlines():
        if "UndefinedTable" in line or "does not exist" in line:
            print("SQL ERR:", line)
    print(tb[-1400:])
