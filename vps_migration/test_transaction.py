#!/usr/bin/env python3
"""E2E transaction test on the VPS: create a Vehicle POS Invoice via create_from_pos(data).
Tests POS/VMS transaction with a real Ultra MRF company (PHP), real customer, vehicle, item.
"""
import frappe, json

frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")

co = frappe.get_all("Company", filters={"is_group": 0, "name": ["like", "Ultra MRF%"]}, limit=1)
co = co[0].name if co else None
veh = frappe.get_all("Customer Vehicle", limit=1)
veh = veh[0].name if veh else None
veh_cust = frappe.get_value("Customer Vehicle", veh, "customer") if veh else None
item = frappe.get_all("Item", filters={"is_sales_item": 1, "disabled": 0}, limit=1)
item = item[0].name if item else None
print("company:", co, "| vehicle:", veh, "| vehicle-owner-customer:", veh_cust, "| item:", item)

from vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice import create_from_pos

payload = {
    "customer": veh_cust,       # real owning customer
    "vehicle": veh,
    "company": co,
    "paid_amount": 100,
    "payment_method": "Cash",
    "items": [{"item_code": item, "qty": 1, "rate": 100, "discount_amount": 0, "uom": "Nos"}],
}

try:
    res = create_from_pos(payload)
    name = res.get("name") if isinstance(res, dict) else res
    print("RESULT:", res)
    print("Vehicle POS Invoice exists:", frappe.db.exists("Vehicle POS Invoice", name))
    # fetch the created doc to see the linked POS Invoice
    if name:
        d = frappe.get_doc("Vehicle POS Invoice", name)
        print("pos_invoice field:", getattr(d, "pos_invoice", None))
        print("docstatus:", d.docstatus)
except Exception as e:
    import traceback
    print("FAIL:", type(e).__name__, str(e)[:400])
    traceback.print_exc()
