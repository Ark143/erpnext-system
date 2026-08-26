"""
Complete transactional generator for ALL modules of Vehicle Management,
Procure-to-Pay (P2P), Order-to-Cash (O2C), Stock Entry & Purchase Receipt
with 50% Sales Person Commission, Inventory Dimension, Bin Locations,
Customer Vehicles across ALL Companies, Branches, and Cost Centers.
"""

import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))

import frappe
from frappe.utils import nowdate, add_days, flt

os.chdir(os.path.join(os.path.dirname(__file__), "sites"))
frappe.init("site1.local")
frappe.connect()

print("=" * 70)
print("  EXECUTING COMPREHENSIVE MULTI-MODULE TRANSACTION GENERATION")
print("=" * 70)

# -------------------------------------------------------------
# 1. SETUP SALES PERSONS & 50% COMMISSION
# -------------------------------------------------------------
SALES_PERSONS = [
    {"name": "Emmanuel Ostria", "company": "Ultra MRF Dau Main"},
    {"name": "Christopher Lucero", "company": "Ultra MRF Dau Annex"},
    {"name": "Karen Cadion", "company": "Ultra MRF San Fernando"},
    {"name": "Jericho Garcia", "company": "Wheel Core"},
    {"name": "Mark Anthony Cruz", "company": "Ultra MRF Telebastagan"},
    {"name": "Jonathan Dizon", "company": "Automan Car Care Center"},
    {"name": "Michael Ramos", "company": "The Wheelhub"},
    {"name": "Reynaldo Santos", "company": "ULTRA MRF"},
    {"name": "Danilo Perez", "company": "Ultra MRF Warehouse Dau"},
    {"name": "Eduardo Tan", "company": "San Fernando Warehouse"},
    {"name": "Ramil Castro", "company": "Ultra MRF Mexico Warehouse"}
]

for sp in SALES_PERSONS:
    sp_name = sp["name"]
    if not frappe.db.exists("Sales Person", sp_name):
        doc = frappe.get_doc({
            "doctype": "Sales Person",
            "sales_person_name": sp_name,
            "parent_sales_person": "Sales Team",
            "commission_rate": 50.0,
            "is_group": 0,
            "enabled": 1
        })
        doc.insert(ignore_permissions=True)
        print(f"  + Created Sales Person: {sp_name} (50% Commission Rate)")
    else:
        frappe.db.set_value("Sales Person", sp_name, "commission_rate", 50.0)

# -------------------------------------------------------------
# 2. SETUP CUSTOMER VEHICLES
# -------------------------------------------------------------
VEHICLE_FLEET = [
    {"plate": "RKH344", "make": "Toyota", "model": "Toyota-Vios", "customer": "BENNY DEL ROSARIO", "year": 2022, "km": 35000},
    {"plate": "NBC-1234", "make": "Toyota", "model": "Toyota-Fortuner", "customer": "BENNY DEL ROSARIO", "year": 2024, "km": 25000},
    {"plate": "CAL-5678", "make": "Mitsubishi", "model": "Mitsubishi-Montero Sport", "customer": "BENNY DEL ROSARIO", "year": 2023, "km": 42000},
    {"plate": "NBD-8899", "make": "Ford", "model": "Ford-Ranger", "customer": "KYLE LHEJ RIMANDO", "year": 2023, "km": 28000},
    {"plate": "NAA-4521", "make": "Honda", "model": "Honda-Civic", "customer": "JOEPET G DAVID", "year": 2021, "km": 45000},
    {"plate": "NDD-7722", "make": "Isuzu", "model": "Isuzu-D-Max", "customer": "GIAN BONDOC", "year": 2022, "km": 38000},
    {"plate": "NCL-3311", "make": "Nissan", "model": "Nissan-Navara", "customer": "HANDRIAN LOR", "year": 2023, "km": 19000},
    {"plate": "NFG-9900", "make": "Toyota", "model": "Toyota-Hilux", "customer": "DANILO OBRA", "year": 2024, "km": 15000},
    {"plate": "NBP-5544", "make": "Toyota", "model": "Toyota-Innova", "customer": "LARIE GUARIN", "year": 2022, "km": 52000},
    {"plate": "NCA-1122", "make": "Honda", "model": "Honda-City", "customer": "JAYVEE M. DIZON", "year": 2020, "km": 61000},
    {"plate": "NDB-3344", "make": "Mitsubishi", "model": "Mitsubishi-Strada / Triton", "customer": "NELSON L. CASTILLO", "year": 2023, "km": 31000}
]

for v in VEHICLE_FLEET:
    if not frappe.db.exists("Customer Vehicle", v["plate"]):
        doc = frappe.get_doc({
            "doctype": "Customer Vehicle",
            "plate_no": v["plate"],
            "customer": v["customer"],
            "make": v["make"],
            "model": v["model"],
            "year_model": v["year"],
            "current_mileage": v["km"],
            "status": "Active"
        })
        doc.insert(ignore_permissions=True)
        print(f"  + Registered Customer Vehicle: {v['plate']} ({v['make']} {v['model']})")

frappe.db.commit()

# -------------------------------------------------------------
# 3. COMPANIES, BRANCHES & COST CENTERS CONFIGURATION
# -------------------------------------------------------------
COMPANIES = [
    {"name": "Ultra MRF Dau Main", "abbr": "UMDM", "sales_person": "Emmanuel Ostria"},
    {"name": "Ultra MRF Dau Annex", "abbr": "UMDA", "sales_person": "Christopher Lucero"},
    {"name": "Ultra MRF San Fernando", "abbr": "UMSF", "sales_person": "Karen Cadion"},
    {"name": "Wheel Core", "abbr": "WCORE", "sales_person": "Jericho Garcia"},
    {"name": "Ultra MRF Telebastagan", "abbr": "UMTEL", "sales_person": "Mark Anthony Cruz"},
    {"name": "Automan Car Care Center", "abbr": "AUTOMAN", "sales_person": "Jonathan Dizon"},
    {"name": "The Wheelhub", "abbr": "WHUB", "sales_person": "Michael Ramos"},
    {"name": "ULTRA MRF", "abbr": "UM", "sales_person": "Reynaldo Santos"},
    {"name": "Ultra MRF Warehouse Dau", "abbr": "UMDW", "sales_person": "Danilo Perez"},
    {"name": "San Fernando Warehouse", "abbr": "SFWH", "sales_person": "Eduardo Tan"},
    {"name": "Ultra MRF Mexico Warehouse", "abbr": "MEXWH", "sales_person": "Ramil Castro"}
]

# Supplier to use
supplier_name = "NGC HARDWARE & CONSTRUCTION SUPPLIES"
if not frappe.db.exists("Supplier", supplier_name):
    supplier_name = frappe.get_all("Supplier", limit=1)[0].name

print("\n" + "-" * 70)
print("  PROCESSING TRANSACTIONS PER COMPANY & BRANCH")
print("-" * 70)

o2c_count = 0
p2p_count = 0
stock_count = 0

for comp in COMPANIES:
    company = comp["name"]
    abbr = comp["abbr"]
    sales_person = comp["sales_person"]
    cost_center = f"Main - {abbr}"
    cash_account = f"Cash - {abbr}"
    debtors_account = f"Debtors - {abbr}"
    creditors_account = f"Creditors - {abbr}"
    sales_account = f"Sales - {abbr}"
    cogs_account = f"Cost of Goods Sold - {abbr}"
    warehouse = f"Stores - {abbr}"

    if not frappe.db.exists("Warehouse", warehouse):
        continue

    # Get active Bin Locations for this warehouse
    bin_locations = frappe.get_all(
        "Bin Location",
        filters={"warehouse": warehouse, "is_active": 1},
        fields=["name", "bin_location_name", "zone"]
    )
    
    bin_a = bin_locations[0].name if len(bin_locations) > 0 else None
    bin_b = bin_locations[1].name if len(bin_locations) > 1 else bin_a
    bin_c = bin_locations[2].name if len(bin_locations) > 2 else bin_a

    # Pick a vehicle from the registered vehicles
    vehicle_info = random.choice(VEHICLE_FLEET)
    plate_no = vehicle_info["plate"]
    customer = vehicle_info["customer"]

    print(f"\n[{company}] (Cost Center: {cost_center} | Warehouse: {warehouse})")

    # =========================================================================
    # A. ORDER-TO-CASH (O2C) / VEHICLE MANAGEMENT FLOW
    # =========================================================================
    try:
        # 1. Vehicle Estimate
        est = frappe.get_doc({
            "doctype": "Vehicle Estimate",
            "company": company,
            "customer": customer,
            "vehicle": plate_no,
            "estimate_date": nowdate(),
            "valid_until": add_days(nowdate(), 15),
            "status": "Approved",
            "services": [
                {
                    "service_item": "WHEEL ALIGNMENT (TOE-IN, TOE-OUT)",
                    "description": "4-WHEEL COMPUTERIZED ALIGNMENT",
                    "hours": 1.5,
                    "rate": 1200.0,
                    "total_amount": 1800.0
                },
                {
                    "service_item": "PMS LABOR (LIGHT)",
                    "description": "PERIODIC MAINTENANCE SERVICE (PMS 20K)",
                    "hours": 2.0,
                    "rate": 950.0,
                    "total_amount": 1900.0
                }
            ],
            "parts": [
                {
                    "item_code": "185/70 R14 YOKOHAMA ES32",
                    "item_name": "185/70 R14 YOKOHAMA ES32 BLUEARTH",
                    "qty": 4,
                    "uom": "PC",
                    "rate": 3650.0,
                    "amount": 14600.0
                },
                {
                    "item_code": "STRL-CAR PROTECT KIT (CAR CLEAN SET)",
                    "item_name": "CAR PROTECTION & CLEAN KIT",
                    "qty": 1,
                    "uom": "PC",
                    "rate": 350.0,
                    "amount": 350.0
                }
            ]
        })
        est.insert(ignore_permissions=True)

        # 2. Vehicle Job Order (Converted from Estimate)
        jo = frappe.get_doc({
            "doctype": "Vehicle Job Order",
            "company": company,
            "customer": customer,
            "vehicle": plate_no,
            "estimate": est.name,
            "cost_center": cost_center,
            "job_order_date": nowdate(),
            "status": "Completed",
            "payment_status": "Paid",
            "services": [
                {
                    "service_item": s.service_item,
                    "description": s.description,
                    "hours": s.hours,
                    "rate": s.rate,
                    "total_amount": s.total_amount
                } for s in est.services
            ],
            "parts": [
                {
                    "item_code": p.item_code,
                    "item_name": p.item_name,
                    "qty": p.qty,
                    "uom": p.uom,
                    "rate": p.rate,
                    "amount": p.amount
                } for p in est.parts
            ]
        })
        jo.insert(ignore_permissions=True)
        frappe.db.set_value("Vehicle Estimate", est.name, "job_order", jo.name)

        # 3. Vehicle Inspection
        insp = frappe.get_doc({
            "doctype": "Vehicle Inspection",
            "company": company,
            "customer": customer,
            "vehicle": plate_no,
            "job_order": jo.name,
            "inspection_date": nowdate(),
            "odometer_reading": vehicle_info["km"] + 150,
            "status": "Completed",
            "overall_summary": "Passed comprehensive multi-point vehicle safety & operational inspection.",
            "items": [
                {"item_name": "Brake Pads & Rotors", "category": "Brakes", "status": "Pass / OK", "observation": "8mm lining remaining"},
                {"item_name": "Tires Condition & Tread Depth", "category": "Tires", "status": "Pass / OK", "observation": "Brand new Yokohama tires installed"},
                {"item_name": "Engine Oil & Fluid Levels", "category": "Engine", "status": "Pass / OK", "observation": "Full synthetic fresh oil"},
                {"item_name": "Battery & Alternator Voltage", "category": "Electrical", "status": "Pass / OK", "observation": "12.8V resting, 14.2V charging"},
                {"item_name": "Wheel Alignment & Suspension", "category": "Underchassis", "status": "Pass / OK", "observation": "Aligned to manufacturer spec"}
            ]
        })
        insp.insert(ignore_permissions=True)

        # 4. Sales Invoice (With 50% Sales Person Commission Allocated)
        grand_total = flt(jo.grand_total)
        commission_allocated = grand_total * 0.50  # 50% commission calculation

        sinv = frappe.get_doc({
            "doctype": "Sales Invoice",
            "company": company,
            "customer": customer,
            "posting_date": nowdate(),
            "due_date": nowdate(),
            "cost_center": cost_center,
            "debit_to": debtors_account,
            "update_stock": 0,
            "items": [
                {
                    "item_code": "185/70 R14 YOKOHAMA ES32",
                    "qty": 4,
                    "rate": 3650.0,
                    "income_account": sales_account,
                    "cost_center": cost_center,
                    "bin_location": bin_b
                },
                {
                    "item_code": "WHEEL ALIGNMENT (TOE-IN, TOE-OUT)",
                    "qty": 1,
                    "rate": 1800.0,
                    "income_account": sales_account,
                    "cost_center": cost_center
                },
                {
                    "item_code": "PMS LABOR (LIGHT)",
                    "qty": 1,
                    "rate": 1900.0,
                    "income_account": sales_account,
                    "cost_center": cost_center
                }
            ],
            "sales_team": [
                {
                    "sales_person": sales_person,
                    "allocated_percentage": 100.0,
                    "commission_rate": 50.0,
                    "allocated_amount": commission_allocated,
                    "incentives": commission_allocated * 0.10
                }
            ]
        })
        sinv.insert(ignore_permissions=True)
        sinv.submit()

        # 5. Payment Entry (Customer Receipt)
        pe_sales = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Receive",
            "party_type": "Customer",
            "party": customer,
            "company": company,
            "paid_from": debtors_account,
            "paid_to": cash_account,
            "paid_amount": sinv.grand_total,
            "received_amount": sinv.grand_total,
            "target_exchange_rate": 1.0,
            "cost_center": cost_center,
            "references": [
                {
                    "reference_doctype": "Sales Invoice",
                    "reference_name": sinv.name,
                    "total_amount": sinv.grand_total,
                    "outstanding_amount": sinv.grand_total,
                    "allocated_amount": sinv.grand_total
                }
            ]
        })
        pe_sales.insert(ignore_permissions=True)
        pe_sales.submit()

        print(f"  [O2C] Estimate ({est.name}) -> JO ({jo.name}) -> Insp ({insp.name}) -> SInv ({sinv.name}) [50% Comm: {sales_person}] -> Pay ({pe_sales.name})")
        frappe.db.commit()
        o2c_count += 1
    except Exception as e:
        frappe.db.rollback()
        print(f"  ! O2C Error in {company}: {e}")

    # =========================================================================
    # B. PROCURE-TO-PAY (P2P) WITH INVENTORY DIMENSION & BIN LOCATIONS
    # =========================================================================
    try:
        # 1. Purchase Order
        po = frappe.get_doc({
            "doctype": "Purchase Order",
            "company": company,
            "supplier": supplier_name,
            "transaction_date": nowdate(),
            "schedule_date": add_days(nowdate(), 3),
            "cost_center": cost_center,
            "items": [
                {
                    "item_code": "185/70 R14 YOKOHAMA ES32",
                    "qty": 8,
                    "rate": 2800.0,
                    "warehouse": warehouse,
                    "cost_center": cost_center,
                    "bin_location": bin_b
                },
                {
                    "item_code": "STRL-CAR PROTECT KIT (CAR CLEAN SET)",
                    "qty": 10,
                    "rate": 150.0,
                    "warehouse": warehouse,
                    "cost_center": cost_center,
                    "bin_location": bin_a
                }
            ]
        })
        po.insert(ignore_permissions=True)
        po.submit()

        # 2. Purchase Receipt (Using Inventory Dimension Bin Location)
        pr = frappe.get_doc({
            "doctype": "Purchase Receipt",
            "company": company,
            "supplier": supplier_name,
            "posting_date": nowdate(),
            "cost_center": cost_center,
            "items": [
                {
                    "purchase_order": po.name,
                    "purchase_order_item": po.items[0].name,
                    "item_code": "185/70 R14 YOKOHAMA ES32",
                    "qty": 8,
                    "rate": 2800.0,
                    "warehouse": warehouse,
                    "cost_center": cost_center,
                    "bin_location": bin_b
                },
                {
                    "purchase_order": po.name,
                    "purchase_order_item": po.items[1].name,
                    "item_code": "STRL-CAR PROTECT KIT (CAR CLEAN SET)",
                    "qty": 10,
                    "rate": 150.0,
                    "warehouse": warehouse,
                    "cost_center": cost_center,
                    "bin_location": bin_a
                }
            ]
        })
        pr.insert(ignore_permissions=True)
        pr.submit()

        # 3. Purchase Invoice (With Inventory Dimension)
        pi = frappe.get_doc({
            "doctype": "Purchase Invoice",
            "company": company,
            "supplier": supplier_name,
            "posting_date": nowdate(),
            "due_date": add_days(nowdate(), 30),
            "cost_center": cost_center,
            "credit_to": creditors_account,
            "items": [
                {
                    "purchase_receipt": pr.name,
                    "pr_detail": pr.items[0].name,
                    "item_code": "185/70 R14 YOKOHAMA ES32",
                    "qty": 8,
                    "rate": 2800.0,
                    "cost_center": cost_center,
                    "expense_account": cogs_account,
                    "bin_location": bin_b
                },
                {
                    "purchase_receipt": pr.name,
                    "pr_detail": pr.items[1].name,
                    "item_code": "STRL-CAR PROTECT KIT (CAR CLEAN SET)",
                    "qty": 10,
                    "rate": 150.0,
                    "cost_center": cost_center,
                    "expense_account": cogs_account,
                    "bin_location": bin_a
                }
            ]
        })
        pi.insert(ignore_permissions=True)
        pi.submit()

        # 4. Payment Entry (Pay Supplier)
        pe_buy = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Pay",
            "party_type": "Supplier",
            "party": supplier_name,
            "company": company,
            "paid_from": cash_account,
            "paid_to": creditors_account,
            "paid_amount": pi.grand_total,
            "received_amount": pi.grand_total,
            "target_exchange_rate": 1.0,
            "cost_center": cost_center,
            "references": [
                {
                    "reference_doctype": "Purchase Invoice",
                    "reference_name": pi.name,
                    "total_amount": pi.grand_total,
                    "outstanding_amount": pi.grand_total,
                    "allocated_amount": pi.grand_total
                }
            ]
        })
        pe_buy.insert(ignore_permissions=True)
        pe_buy.submit()

        print(f"  [P2P] PO ({po.name}) -> PR ({pr.name}) [Bin: {bin_b}] -> PI ({pi.name}) -> Pay ({pe_buy.name})")
        frappe.db.commit()
        p2p_count += 1
    except Exception as e:
        frappe.db.rollback()
        print(f"  ! P2P Error in {company}: {e}")

    # =========================================================================
    # C. STOCK ENTRY (TRANSFER BETWEEN BIN LOCATIONS WITH INVENTORY DIMENSION)
    # =========================================================================
    try:
        se = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Transfer",
            "purpose": "Material Transfer",
            "company": company,
            "from_warehouse": warehouse,
            "to_warehouse": warehouse,
            "posting_date": nowdate(),
            "items": [
                {
                    "item_code": "185/70 R14 YOKOHAMA ES32",
                    "qty": 2,
                    "s_warehouse": warehouse,
                    "t_warehouse": warehouse,
                    "cost_center": cost_center,
                    "bin_location": bin_b,
                    "to_bin_location": bin_c,
                    "basic_rate": 2800.0
                }
            ]
        })
        se.insert(ignore_permissions=True)
        se.submit()
        print(f"  [Stock Entry] {se.name}: Material Transfer [{bin_b} -> {bin_c}]")
        frappe.db.commit()
        stock_count += 1
    except Exception as e:
        frappe.db.rollback()
        print(f"  ! Stock Entry Error in {company}: {e}")

frappe.db.commit()
frappe.clear_cache()

print("\n" + "=" * 70)
print("  TRANSACTION EXECUTION COMPLETED:")
print(f"  - Order-to-Cash (O2C) Full Cycles: {o2c_count} branches")
print(f"  - Procure-to-Pay (P2P) Full Cycles: {p2p_count} branches")
print(f"  - Stock Entries with Bin Dimensions: {stock_count} branches")
print("=" * 70)
