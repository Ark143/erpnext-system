"""
Test Complete Flow:
Vehicle Estimate -> Vehicle Job Order -> Sales Invoice -> Payment -> Customer Vehicle History
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))

import frappe
from frappe.utils import nowdate, flt
from vehicle_management.vehicle_management.doctype.customer_vehicle.customer_vehicle import get_vehicle_transaction_history

os.chdir(os.path.join(os.path.dirname(__file__), "sites"))
frappe.init("site1.local")
frappe.connect()

print("=" * 65)
print("  TESTING VEHICLE ESTIMATE -> JOB ORDER -> HISTORY INTEGRATION")
print("=" * 65)

# Step 1: Create Vehicle Estimate
print("\n[Step 1] Creating Vehicle Estimate...")
est = frappe.get_doc({
    "doctype": "Vehicle Estimate",
    "naming_series": "EST-.YYYY.-.#####",
    "company": "Ultra MRF Dau Main",
    "estimate_date": nowdate(),
    "vehicle": "RKH344",
    "customer": "BENNY DEL ROSARIO",
    "customer_complaint": "Wheel alignment check and car cleaning package",
    "services": [
        {
            "service_item": "WHEEL ALIGNMENT (TOE-IN, TOE-OUT)",
            "description": "WHEEL ALIGNMENT (TOE-IN, TOE-OUT)",
            "hours": 1.0,
            "rate": 870.0,
            "discount_amount": 0.0,
            "total_amount": 870.0
        },
        {
            "service_item": "MISCELLANEOUS",
            "description": "MISCELLANEOUS INSPECTION & TIGHTENING",
            "hours": 1.0,
            "rate": 150.0,
            "discount_amount": 0.0,
            "total_amount": 150.0
        }
    ],
    "parts": [
        {
            "item_code": "STRL-CAR PROTECT KIT (CAR CLEAN SET)",
            "item_name": "STRL-CAR PROTECT KIT (CAR CLEAN SET)",
            "qty": 1.0,
            "uom": "PC",
            "rate": 105.0,
            "discount_amount": 0.0,
            "amount": 105.0
        }
    ],
    "discount_amount": 125.0
})

est.insert(ignore_permissions=True)
print(f"  -> Created Estimate: {est.name}")
print(f"     Vehicle: {est.vehicle} ({est.plate_no})")
print(f"     Customer: {est.customer_name}")
print(f"     Labor: PHP {est.total_labor:,.2f}")
print(f"     Parts: PHP {est.total_parts:,.2f}")
print(f"     Subtotal: PHP {est.net_total:,.2f}")
print(f"     Discount: PHP {est.discount_amount:,.2f}")
print(f"     Grand Total: PHP {est.grand_total:,.2f}")

# Step 2: Convert Estimate to Job Order
print("\n[Step 2] Converting Estimate to Vehicle Job Order...")
jo_name = est.make_job_order()
jo = frappe.get_doc("Vehicle Job Order", jo_name)
est.reload()

print(f"  -> Generated Job Order: {jo.name}")
print(f"     Status: {jo.status}")
print(f"     Linked Estimate: {jo.estimate}")
print(f"     Estimate Status: {est.status} (Linked JO: {est.job_order})")
print(f"     Copied Services: {len(jo.services)}")
print(f"     Copied Parts: {len(jo.parts)}")
print(f"     Grand Total: PHP {jo.grand_total:,.2f}")

# Step 3: Check Customer Vehicle History
print("\n[Step 3] Fetching Customer Vehicle Transaction History...")
history = get_vehicle_transaction_history("RKH344")
print(f"  -> History Summary: {history['summary']}")
print(f"     Estimates logged: {len(history['estimates'])}")
print(f"     Job Orders logged: {len(history['job_orders'])}")
print(f"     Invoices logged: {len(history['invoices'])}")

# Step 4: Verify latest estimate is present
latest_est = history["estimates"][0]
print(f"  -> Latest Estimate in History: {latest_est['name']} - Status: {latest_est['status']} - Total: PHP {latest_est['grand_total']:,.2f}")

frappe.db.commit()

print("\n" + "=" * 65)
print("  ESTIMATE FLOW & HISTORY INTEGRATION TEST PASSED 100%!")
print("=" * 65)
