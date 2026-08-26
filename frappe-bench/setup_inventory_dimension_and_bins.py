"""
Script to create the Inventory Dimension for Bin Location and
populate organized Bin Locations for each company warehouse.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))

import frappe

os.chdir(os.path.join(os.path.dirname(__file__), "sites"))
frappe.init("site1.local")
frappe.connect()

print("=" * 65)
print("  SETUP INVENTORY DIMENSION & BIN LOCATIONS")
print("=" * 65)

# 1. Create or Update Inventory Dimension
DIMENSION_NAME = "Bin Location"
REF_DOCTYPE = "Bin Location"

if frappe.db.exists("Inventory Dimension", {"dimension_name": DIMENSION_NAME}):
    dim = frappe.get_doc("Inventory Dimension", {"dimension_name": DIMENSION_NAME})
    print(f"[Step 1] Inventory Dimension '{DIMENSION_NAME}' already exists.")
else:
    dim = frappe.get_doc({
        "doctype": "Inventory Dimension",
        "dimension_name": DIMENSION_NAME,
        "reference_document": REF_DOCTYPE,
        "apply_to_all_doctypes": 1,
        "validate_negative_stock": 0
    })
    dim.insert(ignore_permissions=True)
    print(f"[Step 1] Created Inventory Dimension '{DIMENSION_NAME}'.")

dim.add_custom_fields()
frappe.db.commit()
print("  -> Custom fields synced across all inventory and transaction DocTypes.")

# 2. Get all non-group Warehouses
warehouses = frappe.get_all(
    "Warehouse",
    filters={"is_group": 0, "disabled": 0},
    fields=["name", "warehouse_name", "company"]
)
print(f"\n[Step 2] Found {len(warehouses)} active storage warehouses.")

# Standard Zones and Layout for Auto Shops & Warehouses
STANDARD_BINS = [
    {
        "zone": "Zone A - Fast Moving & Maintenance",
        "rack": "Rack A1",
        "shelf": "Shelf 1",
        "bin_no": "Bin 01",
        "code_suffix": "A1-S1-01",
        "desc": "Oil Filters, Air Filters, Cabin Filters, Spark Plugs"
    },
    {
        "zone": "Zone A - Fast Moving & Maintenance",
        "rack": "Rack A1",
        "shelf": "Shelf 2",
        "bin_no": "Bin 02",
        "code_suffix": "A1-S2-01",
        "desc": "Wiper Blades, Belts, Bulbs & Small Hardware"
    },
    {
        "zone": "Zone B - Tires & Wheels",
        "rack": "Tire Rack B1",
        "shelf": "Tier 1",
        "bin_no": "Slot 01",
        "code_suffix": "B1-T1-01",
        "desc": "Passenger Car & SUV Tires (Standard Sizes)"
    },
    {
        "zone": "Zone B - Tires & Wheels",
        "rack": "Tire Rack B2",
        "shelf": "Tier 2",
        "bin_no": "Slot 01",
        "code_suffix": "B2-T2-01",
        "desc": "Alloy Wheels, Mags & Heavy Duty Tires"
    },
    {
        "zone": "Zone C - Brakes & Suspension",
        "rack": "Rack C1",
        "shelf": "Shelf 1",
        "bin_no": "Bin 01",
        "code_suffix": "C1-S1-01",
        "desc": "Brake Pads, Brake Shoes, Rotors & Calipers"
    },
    {
        "zone": "Zone C - Brakes & Suspension",
        "rack": "Rack C2",
        "shelf": "Shelf 2",
        "bin_no": "Bin 02",
        "code_suffix": "C2-S2-01",
        "desc": "Shock Absorbers, Struts, Bushings & Ball Joints"
    },
    {
        "zone": "Zone D - Fluids, Oils & Lubricants",
        "rack": "Rack D1",
        "shelf": "Tier 1 (Heavy)",
        "bin_no": "Pallet 01",
        "code_suffix": "D1-T1-01",
        "desc": "Engine Oils (1L & 4L), Synthetic & Mineral"
    },
    {
        "zone": "Zone D - Fluids, Oils & Lubricants",
        "rack": "Rack D1",
        "shelf": "Shelf 2",
        "bin_no": "Bin 02",
        "code_suffix": "D1-S2-02",
        "desc": "Coolants, ATF, Brake Fluids, Gear Oils & Degreasers"
    },
    {
        "zone": "Zone E - Batteries & Electrical",
        "rack": "Rack E1",
        "shelf": "Tier 1 (Heavy)",
        "bin_no": "Slot 01",
        "code_suffix": "E1-T1-01",
        "desc": "Car & Commercial Batteries, Alternators & Starters"
    },
    {
        "zone": "Zone F - Tools, Consumables & PPE",
        "rack": "Rack F1",
        "shelf": "Shelf 1",
        "bin_no": "Bin 01",
        "code_suffix": "F1-S1-01",
        "desc": "Shop Consumables, Protection Kits, Gloves & Cleaners"
    }
]

created_bins = 0
existing_bins = 0

for wh in warehouses:
    wh_name = wh.name
    company = wh.company
    
    # Generate clean warehouse prefix (e.g. UMDM-STORES, UMDA-STORES, WCORE-STORES)
    # Extract abbreviation or prefix
    parts = wh_name.split(" - ")
    if len(parts) >= 2:
        wh_type = parts[0].replace(" ", "").upper()[:6]
        abbr = parts[1].upper()
        prefix = f"{abbr}-{wh_type}"
    else:
        prefix = wh_name.replace(" ", "-").upper()[:12]

    for bin_template in STANDARD_BINS:
        bin_code = f"{prefix}-{bin_template['code_suffix']}"
        
        if frappe.db.exists("Bin Location", bin_code):
            existing_bins += 1
            continue
            
        doc = frappe.get_doc({
            "doctype": "Bin Location",
            "bin_location_name": bin_code,
            "warehouse": wh_name,
            "company": company,
            "zone": bin_template["zone"],
            "rack": bin_template["rack"],
            "shelf": bin_template["shelf"],
            "bin_no": bin_template["bin_no"],
            "barcode": f"BIN-{bin_code}",
            "is_active": 1,
            "description": f"{wh_name} - {bin_template['desc']}"
        })
        doc.insert(ignore_permissions=True)
        created_bins += 1

frappe.db.commit()
frappe.clear_cache()

print("\n" + "=" * 65)
print(f"  BIN LOCATIONS SETUP SUMMARY:")
print(f"  - Newly Created Bins: {created_bins}")
print(f"  - Existing Bins: {existing_bins}")
print(f"  - Total Active Bins in System: {created_bins + existing_bins}")
print(f"  - Covering Warehouses: {len(warehouses)}")
print("=" * 65)
