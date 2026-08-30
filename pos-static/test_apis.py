import frappe, json, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
frappe.session.user = "Administrator"
apis = ["vm_pos_history","vm_pos_cashier","vm_pos_stock","vm_pos_vehicle_customer",
        "vm_pos_vehicles","vm_pos_items","vm_pos_meta","executive_dashboard",
        "vm_company_dashboard_api","vm_probe_api"]
for m in apis:
    try:
        res = frappe.call(m)
        # res may be dict/list
        if isinstance(res, (dict, list)):
            n = len(res) if isinstance(res, list) else len(res.get("message", res))
            print(f"OK   {m}: type={type(res).__name__} size={n}")
        else:
            print(f"OK   {m}: {str(res)[:60]}")
    except Exception as e:
        print(f"FAIL {m}: {type(e).__name__}: {str(e)[:150]}")
