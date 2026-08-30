import frappe, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect(); frappe.set_user("Administrator")
for dt in ["Customer","Item","Sales Invoice","Vehicle","Employee"]:
    try:
        n=frappe.db.count(dt)
        sample=frappe.get_list(dt, fields=["name"], limit=1)
        print(f"{dt}: count={n} sample={sample}")
    except Exception as e:
        print(f"{dt}: ERROR {str(e)[:120]}")
