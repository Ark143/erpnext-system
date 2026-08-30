import frappe, json, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
frappe.session.user = "Administrator"
from frappe.core.doctype.server_script.server_script_utils import run_server_script
names = {"vm_pos_history":"VM POS History","vm_pos_cashier":"VM POS Cashier","vm_pos_stock":"VM POS Stock",
         "vm_pos_vehicle_customer":"VM POS Vehicle Customer","vm_pos_vehicles":"VM POS Vehicles",
         "vm_pos_items":"VM POS Items","vm_pos_meta":"VM POS Meta","executive_dashboard":"Executive Dashboard API",
         "vm_company_dashboard_api":"VM Company Dashboard API","vm_probe_api":"Probe API"}
for api, name in names.items():
    try:
        frappe.form_dict = frappe._dict({})
        res = run_server_script(api_method=api)
        sz = len(res) if isinstance(res,(list,dict)) else (len(res.get("message",res)) if isinstance(res,dict) else 0)
        print(f"OK   {api}: size={sz}")
    except Exception as e:
        print(f"FAIL {api}: {type(e).__name__}: {str(e)[:140]}")
