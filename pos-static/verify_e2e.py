import frappe, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()

# Use a REAL vehicle that has a linked customer (from earlier: NDB-3344 -> NELSON L. CASTILLO)
veh = frappe.get_all("Customer Vehicle", fields=["name","customer","make","model","year_model","plate_no"], limit=1)[0]
print("vehicle:", veh)
cust = veh["customer"]
co = "Ultra MRF Dau Main"
item = frappe.get_all("Item", filters={"is_sales_item":1,"disabled":0}, limit=1)[0].name

from vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice import create_from_pos
payload = {"customer": cust, "vehicle": veh["name"], "company": co, "paid_amount": 200, "payment_method":"Cash",
           "items":[{"item_code":item,"qty":1,"rate":200,"discount_amount":0,"uom":"Nos"}]}
try:
    frappe.db.rollback()
    res = create_from_pos(payload)
    name = res.get("name")
    exists = frappe.db.exists("Vehicle POS Invoice", name)
    doc = frappe.get_doc("Vehicle POS Invoice", name) if exists else None
    print("RESULT:", res)
    print("VMSPOS exists:", exists, "| customer:", doc.customer if doc else None, "| vehicle:", doc.vehicle if doc else None, "| docstatus:", doc.docstatus if doc else None)
    # the KEY assertion: vehicle link is captured on the created invoice
    print("LINK CHECK -> vehicle on invoice ==", doc.vehicle if doc else None, "expected", veh["name"])
    # cleanup: cancel the test invoice so env stays tidy
    if exists:
        try:
            frappe.get_doc("Vehicle POS Invoice", name).cancel()
        except Exception as e:
            print("cancel note:", repr(e)[:120])
    frappe.db.commit()
    print("cleanup done; VMSPOS exists after cancel:", frappe.db.exists("Vehicle POS Invoice", name))
except Exception as e:
    print("OUTER ERROR:", repr(e)[:300])
    traceback.print_exc()
finally:
    frappe.db.rollback()
