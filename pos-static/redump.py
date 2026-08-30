import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
for name in ["Executive Dashboard API","VM Company Dashboard API"]:
    d = frappe.get_doc("Server Script", name)
    open("/tmp/live_"+name.replace(" ","_")+".txt","w").write(d.script)
    print(name, "saved")
