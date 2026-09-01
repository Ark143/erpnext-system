import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# Force-close the stale outdated open POS Opening Entry (dev/test data; erp_pg backed up)
frappe.db.sql(
    'UPDATE "tabPOS Opening Entry" SET docstatus=2, status=%s WHERE name=%s',
    ("Closed", "POS-OPE-2026-00001"),
)
frappe.db.commit()
print("closed POS-OPE-2026-00001 ->", frappe.get_value("POS Opening Entry", "POS-OPE-2026-00001", ["status","docstatus"]))
print("remaining open:", frappe.get_all("POS Opening Entry", {"status":"Open","docstatus":1}, "name"))
