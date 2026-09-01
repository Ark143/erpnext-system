import frappe, psycopg2
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()

# Wrap db.sql to surface the FIRST real DB error (before transaction abort hides it)
orig_sql = frappe.db.sql
def patched_sql(query, *a, **k):
    try:
        return orig_sql(query, *a, **k)
    except psycopg2.Error as e:
        print("!!! FIRST DB ERROR:", repr(str(e).strip()[:600]))
        print("!!! SQL WAS:", (query[:400] if isinstance(query,str) else query))
        raise
frappe.db.sql = patched_sql

co = "Ultra MRF Dau Main"
veh = frappe.get_all("Customer Vehicle", fields=["name","customer"], limit=1)[0]
vcust = veh["customer"]
item = frappe.get_all("Item", filters={"is_sales_item":1,"disabled":0}, limit=1)[0].name
from vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice import create_from_pos
payload = {"customer": vcust, "vehicle": veh["name"], "company": co, "paid_amount": 150, "payment_method":"Cash",
           "items":[{"item_code":item,"qty":1,"rate":150,"discount_amount":0,"uom":"Nos"}]}
try:
    frappe.db.rollback()
    res = create_from_pos(payload)
    print("RESULT:", res)
except Exception as e:
    print("OUTER ERR:", repr(e)[:200])
finally:
    frappe.db.rollback()
