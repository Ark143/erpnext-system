import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# Check doctype existence and table existence separately (fresh, no cascade)
for dt in ["Vehicle Job Order Item","Customer Vehicle","Vehicle Make","Vehicle Model","Bin Location","Bin"]:
    exists_dt = frappe.db.exists("DocType", dt)
    print(f"DocType {dt}: {'EXISTS' if exists_dt else 'MISSING'}")
    if exists_dt:
        try:
            frappe.db.sql(f'SELECT 1 FROM "tab{dt}" LIMIT 1', as_dict=True)
            print(f"   table: EXISTS")
        except Exception as e:
            print(f"   table: MISSING ({type(e).__name__})")
