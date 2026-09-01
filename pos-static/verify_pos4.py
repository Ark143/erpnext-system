import frappe, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
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
    print("RESULT:", res, "exists:", frappe.db.exists("Vehicle POS Invoice", res.get("name")))
    if res.get("name"):
        frappe.delete_doc("Vehicle POS Invoice", res["name"], force=True); frappe.db.commit()
        print("cleaned up:", res["name"])
except Exception as e:
    frappe.db.rollback()
    print("=== DEEP TRACEBACK ===")
    print(frappe.get_traceback() if hasattr(frappe,"get_traceback") else traceback.format_exc())
