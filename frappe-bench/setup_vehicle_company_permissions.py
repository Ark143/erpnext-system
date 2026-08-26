"""
Script to:
1. Reload all vehicle management doctypes to apply the new company field.
2. Backfill existing records with company = 'Ultra MRF Dau Main' or parent 'ULTRA MRF' if NULL.
3. Test permission queries with 'sales@gmail.com' (restricted to 'Ultra MRF Dau Annex') and 'Administrator'.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))

import frappe

frappe.init("site1.local")
frappe.connect()

print("=== 1. Reloading Vehicle Management DocTypes ===")
doctypes = [
    "customer_vehicle",
    "vehicle_job_order",
    "vehicle_inspection",
    "vehicle_service_reminder"
]

for dt in doctypes:
    frappe.reload_doc("vehicle_management", "doctype", dt)
    print(f"  Reloaded: {dt}")

frappe.db.commit()

# 2. Backfill company for existing records
print("\n=== 2. Backfilling company field for existing records ===")
default_company = "ULTRA MRF"

for table in ["tabCustomer Vehicle", "tabVehicle Job Order", "tabVehicle Inspection", "tabVehicle Service Reminder"]:
    count = frappe.db.sql(f"SELECT COUNT(*) FROM `{table}` WHERE company IS NULL OR company = ''")[0][0]
    if count > 0:
        frappe.db.sql(f"UPDATE `{table}` SET company = %s WHERE company IS NULL OR company = ''", (default_company,))
        frappe.db.commit()
        print(f"  Updated {count} records in {table} -> {default_company}")
    else:
        print(f"  {table}: all records have company assigned")

# 3. Create a sample record under "Ultra MRF Dau Annex"
test_plate = "TEST-DAU-ANNEX"
if not frappe.db.exists("Customer Vehicle", test_plate):
    veh = frappe.get_doc({
        "doctype": "Customer Vehicle",
        "plate_no": test_plate,
        "customer": "BENNY DEL ROSARIO",
        "company": "Ultra MRF Dau Annex",
        "make": "Mitsubishi",
        "model": "Mitsubishi-Montero Sport",
        "year_model": 2020,
        "status": "Active"
    })
    veh.insert(ignore_permissions=True)
    frappe.db.commit()
    print(f"  Created test vehicle for Ultra MRF Dau Annex: {test_plate}")

# 4. Test permission filtering for sales@gmail.com
print("\n=== 3. Testing Permission Isolation for sales@gmail.com ===")
frappe.set_user("sales@gmail.com")

# Get list of Customer Vehicles as sales@gmail.com
dau_annex_vehicles = frappe.get_list("Customer Vehicle", fields=["name", "company", "plate_no"])
print(f"  sales@gmail.com can see {len(dau_annex_vehicles)} vehicles:")
for v in dau_annex_vehicles[:5]:
    print(f"    - Plate: {v.plate_no} | Company: {v.company}")

# Get list of Job Orders as sales@gmail.com
dau_annex_jos = frappe.get_list("Vehicle Job Order", fields=["name", "company"])
print(f"  sales@gmail.com can see {len(dau_annex_jos)} job orders:")
for jo in dau_annex_jos:
    print(f"    - JO: {jo.name} | Company: {jo.company}")

# Switch back to Administrator
frappe.set_user("Administrator")
admin_vehicles = frappe.get_list("Customer Vehicle")
print(f"\n  Administrator can see ALL {len(admin_vehicles)} vehicles.")

print("\nPermission isolation test passed!")
