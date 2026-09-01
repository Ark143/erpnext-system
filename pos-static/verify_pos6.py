import frappe, psycopg2, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()

orig_sql = frappe.db.sql
def patched_sql(query, *a, **k):
    try:
        return orig_sql(query, *a, **k)
    except psycopg2.Error as e:
        print("!!! FIRST DB ERROR:", repr(str(e).strip()[:500]))
        # print a short stack to see who built this SQL
        import inspect
        for frame in inspect.stack()[1:8]:
            print(f"   {frame.filename}:{frame.lineno} in {frame.function}")
        raise
frappe.db.sql = patched_sql

co = "Ultra MRF Dau Main"
veh = frappe.get_all("Customer Vehicle", fields=["name","customer"], limit=1)[0]
item = frappe.get_all("Item", filters={"is_sales_item":1,"disabled":0}, limit=1)[0].name
from vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice import create_from_pos
payload = {"customer": veh["customer"], "vehicle": veh["name"], "company": co, "paid_amount": 150, "payment_method":"Cash",
           "items":[{"item_code":item,"qty":1,"rate":150,"discount_amount":0,"uom":"Nos"}]}
try:
    frappe.db.rollback()
    res = create_from_pos(payload)
    print("RESULT:", res)
except Exception as e:
    print("OUTER:", repr(e)[:200])
finally:
    frappe.db.rollback()
