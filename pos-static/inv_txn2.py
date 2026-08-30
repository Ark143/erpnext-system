import frappe, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
print("=== Transaction creation (clean) ===")
try:
    cust = frappe.get_all("Customer", filters=[["customer_name","like","%CHIIETE%"]], limit=1, pluck="name")
    item = frappe.get_all("Item", filters={"is_sales_item":1,"disabled":0}, limit=1, pluck="name")
    wh = frappe.get_all("Warehouse", filters={"company":"ULTRA MRF"}, limit=1, pluck="name")
    print("  cust=%s item=%s wh=%s" % (cust, item, wh))
    if cust and item and wh:
        so = frappe.get_doc({
            "doctype":"Sales Order","customer":cust[0],"company":"ULTRA MRF",
            "delivery_date":"2026-12-31",
            "items":[{"item_code":item[0],"qty":1,"rate":100,"warehouse":wh[0]}]
        })
        so.insert(ignore_permissions=True)
        print("  Sales Order created:", so.name, "-> then deleted")
        frappe.delete_doc("Sales Order", so.name, ignore_permissions=True, force=True)
    # Purchase Order
    supp = frappe.get_all("Supplier", limit=1, pluck="name")
    if supp and item and wh:
        po = frappe.get_doc({
            "doctype":"Purchase Order","supplier":supp[0],"company":"ULTRA MRF",
            "schedule_date":"2026-12-31",
            "items":[{"item_code":item[0],"qty":1,"rate":80,"warehouse":wh[0]}]
        })
        po.insert(ignore_permissions=True)
        print("  Purchase Order created:", po.name, "-> then deleted")
        frappe.delete_doc("Purchase Order", po.name, ignore_permissions=True, force=True)
    print("TRANSACTION TEST PASSED")
except Exception:
    print("TRANSACTION TEST FAILED:")
    print(traceback.format_exc()[-2000:])
