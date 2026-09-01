import frappe, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
item = frappe.get_all("Item", filters={"is_sales_item":1,"disabled":0}, limit=1)[0].name
try:
    inv = frappe.get_doc({
        "doctype":"POS Invoice","company":"My Company",
        "customer":"NELSON L. CASTILLO",
        "posting_date":"2026-08-30",
        "items":[{"item_code":item,"qty":1,"rate":100,"uom":"Nos"}],
        "payments":[{"mode_of_payment":"Cash","amount":100}],
    })
    print("POS Invoice currency before insert:", inv.currency)
    inv.insert()
    print("INSERTED OK currency:", inv.currency)
    inv.cancel()
except Exception as e:
    traceback.print_exc()
    print("ERR:", repr(e))
