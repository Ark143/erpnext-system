import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
for name in ["Executive Dashboard API","VM Company Dashboard API"]:
    d = frappe.get_doc("Server Script", name)
    open("/tmp/ss_"+name.replace(" ","_")+".txt","w").write(d.script)
    print(name, "lines=", len(d.script.splitlines()))
# Also dump schema of tables referenced in company dashboard
for t in ["tabVehicle Job Order","tabJob Order Service Item","tabJob Order Part Item","tabVehicle Estimate","tabVehicle Inspection","tabSales Invoice","tabCustomer Vehicle"]:
    try:
        cols = frappe.db.sql("SELECT column_name FROM information_schema.columns WHERE table_name=%s ORDER BY ordinal_position", t, as_dict=True)
        print(f"\n{t} ({len(cols)} cols):", [c['column_name'] for c in cols])
    except Exception as e:
        print(f"\n{t}: ERR {e}")
