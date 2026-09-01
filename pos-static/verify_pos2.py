import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# GL entries on Debtors - MC?
n = frappe.db.count("GL Entry", {"account":"Debtors - MC"}) if frappe.db.exists("GL Entry") else -1
print("GL Entry count for Debtors - MC:", n)
# also any Journal/ledger referencing it
# Verify transaction works with a real PHP Ultra MRF company + a vehicle whose customer is PHP
co = "Ultra MRF Dau Main"
cust = frappe.get_all("Customer", filters={"default_currency":["in",["","NULL",None]]}, limit=1)
print("php-null customer sample:", cust[:1])
# pick a Customer Vehicle and its customer
veh = frappe.get_all("Customer Vehicle", fields=["name","customer"], limit=1)
print("vehicle:", veh)
vcust = veh[0]["customer"] if veh else None
print("vehicle customer:", vcust, "currency:", frappe.db.get_value("Customer", vcust, "default_currency") if vcust else None)
item = frappe.get_all("Item", filters={"is_sales_item":1,"disabled":0}, limit=1)[0].name
from vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice import create_from_pos
payload = {"customer": vcust, "vehicle": veh[0]["name"], "company": co, "paid_amount": 150, "payment_method":"Cash",
           "items":[{"item_code":item,"qty":1,"rate":150,"discount_amount":0,"uom":"Nos"}]}
try:
    res = create_from_pos(payload)
    print("RESULT:", res, "exists:", frappe.db.exists("Vehicle POS Invoice", res.get("name")))
    if res.get("name"):
        frappe.delete_doc("Vehicle POS Invoice", res["name"], force=True); frappe.db.commit()
        print("cleaned up test invoice")
except Exception as e:
    import traceback; traceback.print_exc(); print("ERR:", repr(e))
