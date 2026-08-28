import sys, os, random
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')
import frappe
from frappe.utils import nowdate, now_datetime, getdate, add_days

frappe.init(site='erp.localhost')
frappe.connect()

companies = frappe.get_list("Company", filters={"name": ["!=", "My Company"]}, pluck="name")
items = frappe.get_list("Item", filters={"is_sales_item": 1}, pluck="name")
suppliers = frappe.get_list("Supplier", pluck="name")
customers = frappe.get_list("Customer", pluck="name")
vehicles = frappe.get_list("Customer Vehicle", pluck="name")

print(f"Generating pending approval drafts across {len(companies)} companies...")

created_count = 0

for co in companies:
    co_abbr = frappe.db.get_value("Company", co, "abbr")
    
    # 1. Draft Vehicle Job Orders (1-2 per company)
    for _ in range(random.randint(1, 2)):
        v = random.choice(vehicles)
        cust = random.choice(customers)
        vjo = frappe.new_doc("Vehicle Job Order")
        vjo.company = co
        vjo.customer = cust
        vjo.vehicle = v
        vjo.job_order_date = add_days(nowdate(), -random.randint(0, 4))
        vjo.service_type = random.choice(["Preventive Maintenance", "Brake System Repair", "Tire Replacement & Balancing", "Engine Diagnostics"])
        vjo.description = f"Regular {vjo.service_type} and multi-point checkup"
        vjo.status = "Draft"
        vjo.promised_delivery_date = add_days(nowdate(), random.randint(1, 4))
        
        it = random.choice(items)
        vjo.append("services", {
            "service_item": it,
            "description": f"Service: {it}",
            "qty": random.randint(1, 4),
            "rate": random.choice([850.0, 1500.0, 2800.0, 4500.0, 6200.0]),
            "service_type": "Labor"
        })
        vjo.flags.ignore_links = True
        vjo.insert(ignore_permissions=True)
        created_count += 1

    # 2. Draft Purchase Orders (1-2 per company)
    if suppliers and items:
        for _ in range(random.randint(1, 2)):
            supp = random.choice(suppliers)
            po = frappe.new_doc("Purchase Order")
            po.company = co
            po.supplier = supp
            po.transaction_date = add_days(nowdate(), -random.randint(1, 10))
            po.schedule_date = add_days(nowdate(), random.randint(2, 7))
            it = random.choice(items)
            wh = frappe.db.get_value("Warehouse", {"company": co, "is_group": 0}, "name") or ("Stores - " + co_abbr)
            po.append("items", {
                "item_code": it,
                "qty": random.randint(4, 25),
                "rate": random.choice([450.0, 850.0, 1500.0, 3200.0]),
                "warehouse": wh,
                "schedule_date": add_days(nowdate(), random.randint(2, 7))
            })
            po.flags.ignore_links = True
            po.insert(ignore_permissions=True)
            created_count += 1

    # 3. Draft Sales Invoices (1-2 per company)
    if customers and items:
        cust = random.choice(customers)
        si = frappe.new_doc("Sales Invoice")
        si.company = co
        si.customer = cust
        si.posting_date = add_days(nowdate(), -random.randint(0, 3))
        it = random.choice(items)
        si.append("items", {
            "item_code": it,
            "qty": random.randint(1, 3),
            "rate": random.choice([950.0, 1800.0, 3200.0, 5400.0]),
            "income_account": frappe.db.get_value("Account", {"company": co, "account_type": "Income Account", "is_group": 0}, "name") or "Sales - " + co_abbr,
            "cost_center": frappe.db.get_value("Cost Center", {"company": co, "is_group": 0}, "name") or "Main - " + co_abbr
        })
        si.flags.ignore_links = True
        si.insert(ignore_permissions=True)
        created_count += 1

    # 4. Draft Material Requests (1 per company)
    if items:
        it = random.choice(items)
        mr = frappe.new_doc("Material Request")
        mr.company = co
        mr.material_request_type = "Purchase"
        mr.transaction_date = add_days(nowdate(), -random.randint(1, 6))
        mr.schedule_date = add_days(nowdate(), random.randint(3, 10))
        wh = frappe.db.get_value("Warehouse", {"company": co, "is_group": 0}, "name") or ("Stores - " + co_abbr)
        mr.append("items", {
            "item_code": it,
            "qty": random.randint(10, 50),
            "warehouse": wh,
            "schedule_date": add_days(nowdate(), random.randint(3, 10))
        })
        mr.flags.ignore_links = True
        mr.insert(ignore_permissions=True)
        created_count += 1

frappe.db.commit()
print(f"SUCCESS! Generated {created_count} draft approval documents across all {len(companies)} companies!")
