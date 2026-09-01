import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
val = "POS-CLO-2026-00001"
# search child tables / link fields referencing it
tables = [
    "tabPOS Invoice Reference", "tabSales Invoice Reference",
    "tabPOS Closing Entry", "tabPOS Opening Entry",
    "tabPayment Reconciliation", "tabPayment Entry Reference",
]
for t in tables:
    try:
        rows = frappe.db.sql(f"SELECT * FROM \"{t}\" WHERE \"{t}\"::text LIKE %s LIMIT 5", (f"%{val}%",), as_dict=1)
        if rows:
            print(t, "->", len(rows), "rows")
    except Exception as e:
        pass
# also search any column named pos_closing_entry across common tables
for t in ["tabPOS Opening Entry","tabPOS Invoice","tabSales Invoice"]:
    try:
        r = frappe.db.sql(f"SELECT name, pos_closing_entry FROM \"{t}\" WHERE pos_closing_entry=%s", (val,), as_dict=1)
        if r: print(t, "pos_closing_entry match:", r)
    except Exception: pass
print("done")
