import frappe, psycopg2, inspect, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()

# Patch execute_query to surface the FIRST real DB error (before frappe re-raises as wrapped)
orig_exec = frappe.db.execute_query
_seen = {}
def patched_exec(query, values=None, *a, **k):
    try:
        return orig_exec(query, values, *a, **k)
    except Exception as e:
        msg = str(e).strip()[:600]
        key = msg[:80]
        if key not in _seen:
            _seen[key] = 1
            print("!!! FIRST DB ERROR:", repr(msg))
            print("!!! QUERY:", (query[:400] if isinstance(query, str) else str(query)[:400]))
            for fr in inspect.stack()[1:9]:
                print(f"   {fr.filename}:{fr.lineno} in {fr.function}")
        raise
frappe.db.execute_query = patched_exec

co = "Ultra MRF Dau Main"
veh = frappe.get_all("Customer Vehicle", fields=["name","customer"], limit=1)[0]
item = frappe.get_all("Item", filters={"is_sales_item":1,"disabled":0}, limit=1)[0].name
from vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice import create_from_pos
payload = {"customer": veh["customer"], "vehicle": veh["name"], "company": co, "paid_amount": 150, "payment_method":"Cash",
           "items":[{"item_code":item,"qty":1,"rate":150,"discount_amount":0,"uom":"Nos"}]}
try:
    frappe.db.rollback()
    res = create_from_pos(payload)
    print("RESULT:", res, "exists:", frappe.db.exists("Vehicle POS Invoice", res.get("name")))
    if res.get("name"):
        frappe.delete_doc("Vehicle POS Invoice", res["name"], force=True); frappe.db.commit()
        print("cleaned up:", res["name"])
except Exception as e:
    print("OUTER:", repr(e)[:300])
finally:
    frappe.db.rollback()
