import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
val = "POS-CLO-2026-00001"
# find tables/columns that reference pos_closing_entry
cols = frappe.db.sql("""
  SELECT table_name, column_name FROM information_schema.columns
  WHERE column_name='pos_closing_entry' AND table_schema='public'
""", as_dict=1)
print("cols named pos_closing_entry:", cols)
for c in cols:
    t = c["table_name"]
    try:
        r = frappe.db.sql(f'SELECT name, "{c["column_name"]}" FROM "{t}" WHERE "{c["column_name"]}"=%s', (val,), as_dict=1)
        if r: print(t, "->", r)
    except Exception as e:
        print("err", t, repr(e)[:120])
frappe.db.rollback()
# also search payment reconciliation / pos invoice reference tables for the value as text
for t in ["tabPOS Invoice Reference","tabSales Invoice Reference","tabPOS Closing Entry","tabPOS Opening Entry"]:
    for col in ["pos_closing_entry","closing_entry","parent","reference_name"]:
        try:
            r = frappe.db.sql(f'SELECT name FROM "{t}" WHERE "{col}"=%s', (val,), as_dict=1)
            if r: print(t, col, "->", r[:3])
        except Exception: pass
frappe.db.rollback()
print("done")
