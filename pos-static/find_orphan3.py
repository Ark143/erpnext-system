import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# inspect the stale opening entry's pos_closing_entry + status
for t in ["tabPOS Opening Entry","tabSales Invoice"]:
    try:
        r = frappe.db.sql(f'SELECT name, pos_closing_entry, status, docstatus FROM "{t}" WHERE pos_closing_entry=%s', ("POS-CLO-2026-00001",), as_dict=1)
        print(t, "with pos_closing_entry=POS-CLO-2026-00001:", r)
    except Exception as e:
        print(t, "err", repr(e)[:120])
    frappe.db.rollback()
# does POS-CLO-2026-00001 exist at all?
print("exists POS-CLO-2026-00001:", frappe.db.exists("POS Closing Entry", "POS-CLO-2026-00001"))
# any open entries now
print("open entries:", frappe.get_all("POS Opening Entry", {"status":"Open","docstatus":1}, ["name","pos_closing_entry","period_start_date"]))
