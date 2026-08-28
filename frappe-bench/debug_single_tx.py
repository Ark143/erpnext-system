import sys, os, traceback
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
os.chdir('sites')
import frappe
from frappe.utils import nowdate, add_days

frappe.init(site='erp.localhost')
frappe.connect()

co = "Ultra MRF Dau Main"
co_abbr = frappe.db.get_value("Company", co, "abbr")
customer = frappe.get_list("Customer", pluck="name")[0]
supplier = frappe.get_list("Supplier", pluck="name")[0]
item_code = frappe.get_list("Item", filters={"is_sales_item": 1, "is_stock_item": 1}, pluck="name")[0]
wh = frappe.get_list("Warehouse", filters={"company": co, "is_group": 0}, pluck="name")[0]

print(f"Testing 1 O2C cycle for {co}...")
try:
    so = frappe.new_doc("Sales Order")
    so.company = co
    so.customer = customer
    so.transaction_date = nowdate()
    so.delivery_date = add_days(nowdate(), 2)
    so.append("items", {
        "item_code": item_code,
        "qty": 1,
        "rate": 1500.0,
        "warehouse": wh,
        "delivery_date": add_days(nowdate(), 2)
    })
    so.insert(ignore_permissions=True)
    so.submit()
    print("Sales Order SUCCESS:", so.name)
except Exception as e:
    print("Sales Order FAILED:", e)
    traceback.print_exc()

print(f"\nTesting 1 P2P cycle for {co}...")
try:
    po = frappe.new_doc("Purchase Order")
    po.company = co
    po.supplier = supplier
    po.transaction_date = nowdate()
    po.schedule_date = add_days(nowdate(), 3)
    po.append("items", {
        "item_code": item_code,
        "qty": 5,
        "rate": 800.0,
        "warehouse": wh,
        "schedule_date": add_days(nowdate(), 3)
    })
    po.insert(ignore_permissions=True)
    po.submit()
    print("Purchase Order SUCCESS:", po.name)
except Exception as e:
    print("Purchase Order FAILED:", e)
    traceback.print_exc()

print(f"\nTesting 1 Stock Entry for {co}...")
try:
    se = frappe.new_doc("Stock Entry")
    se.purpose = "Material Receipt"
    se.company = co
    se.posting_date = nowdate()
    se.to_warehouse = wh
    se.append("items", {
        "item_code": item_code,
        "qty": 10,
        "t_warehouse": wh,
        "basic_rate": 500.0
    })
    se.insert(ignore_permissions=True)
    se.submit()
    print("Stock Entry SUCCESS:", se.name)
except Exception as e:
    print("Stock Entry FAILED:", e)
    traceback.print_exc()
