import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# ---- verify the CSS edit persisted ----
p = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/page/vehicle_pos/vehicle_pos.js"
src = open(p, encoding="utf-8").read()
print("grid 50/50 present:", "grid-template-columns: 220px 1fr 1fr" in src)
print("order flex:none present:", "flex: none; grid-column: 3" in src)
print("responsive present:", "@media (max-width: 768px)" in src)
print("no fixed 380px order:", "flex: 0 0 380px" not in src)

# ---- verify transaction: create_from_pos actually creates an invoice ----
from vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice import create_from_pos
cust = frappe.get_all("Customer", limit=1)[0].name
veh_rows = frappe.get_all("Customer Vehicle", limit=1)
veh = veh_rows[0].name if veh_rows else None
item = frappe.get_all("Item", filters={"is_sales_item":1,"disabled":0}, limit=1)[0].name
co = frappe.get_all("Company", filters={"is_group":0}, limit=1)[0].name
print("using:", cust, veh, item, co)
payload = {
  "customer": cust,
  "vehicle": veh,
  "company": co,
  "paid_amount": 100,
  "payment_method": "Cash",
  "items": [{"item_code": item, "qty": 1, "rate": 100, "discount_amount": 0, "uom": "Nos"}]
}
try:
    res = create_from_pos(payload)
    print("create_from_pos RESULT:", res)
    name = (res or {}).get("name")
    print("exists in DB:", frappe.db.exists("Vehicle POS Invoice", name))
    # cleanup the test invoice so we don't pollute
    if name and frappe.db.exists("Vehicle POS Invoice", name):
        frappe.delete_doc("Vehicle POS Invoice", name, force=True)
        frappe.db.commit()
        print("test invoice cleaned up:", name)
except Exception as e:
    import traceback; traceback.print_exc()
    print("TRANSACTION ERROR:", repr(e))
