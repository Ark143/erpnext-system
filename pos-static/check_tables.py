import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
tables = ["tabVehicle Job Order","tabVehicle Estimate","tabVehicle Inspection","tabVehicle Job Order Item",
          "tabCustomer Vehicle","tabVehicle Make","tabVehicle Model","tabBin Location","tabBin"]
for t in tables:
    try:
        c = frappe.db.sql(f'SELECT 1 FROM "{t}" LIMIT 1', as_dict=True)
        print(f"EXISTS  {t}")
    except Exception as e:
        print(f"MISSING {t}: {type(e).__name__}")
