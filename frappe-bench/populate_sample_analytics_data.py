"""
Script to create realistic sample Job Orders and Services across all branches
covering Tires, Mags, Brake Services, Alignments, Oil Changes, etc.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))

import frappe
from frappe.utils import nowdate, add_days

os.chdir(os.path.join(os.path.dirname(__file__), "sites"))
frappe.init("site1.local")
frappe.connect()

print("=" * 65)
print("  POPULATING RICH SAMPLE ANALYTICS TRANSACTIONS")
print("=" * 65)

# Ensure sample customer vehicle
if not frappe.db.exists("Customer Vehicle", "NBC-1234"):
    v = frappe.get_doc({
        "doctype": "Customer Vehicle",
        "plate_no": "NBC-1234",
        "customer": "BENNY DEL ROSARIO",
        "make": "Toyota",
        "model": "Toyota-Fortuner",
        "year_model": 2024,
        "current_mileage": 25000,
        "status": "Active"
    })
    v.insert(ignore_permissions=True)

if not frappe.db.exists("Customer Vehicle", "CAL-5678"):
    v = frappe.get_doc({
        "doctype": "Customer Vehicle",
        "plate_no": "CAL-5678",
        "customer": "BENNY DEL ROSARIO",
        "make": "Mitsubishi",
        "model": "Mitsubishi-Montero Sport",
        "year_model": 2023,
        "current_mileage": 42000,
        "status": "Active"
    })
    v.insert(ignore_permissions=True)

SAMPLE_JOBS = [
    {
        "company": "Ultra MRF San Fernando",
        "vehicle": "RKH344",
        "date": add_days(nowdate(), -2),
        "status": "Completed",
        "services": [
            {"service_item": "WHEEL ALIGNMENT (TOE-IN, TOE-OUT)", "description": "WHEEL ALIGNMENT (TOE-IN, TOE-OUT)", "hours": 1.5, "rate": 1200.0, "amount": 1800.0},
            {"service_item": "PMS LABOR (LIGHT)", "description": "PREVENTIVE MAINTENANCE (PMS 20K)", "hours": 2.0, "rate": 950.0, "amount": 1900.0}
        ],
        "parts": [
            {"item_code": "185/70 R14 YOKOHAMA ES32", "item_name": "185/70 R14 YOKOHAMA ES32 BLUEARTH", "qty": 4, "uom": "PC", "rate": 3650.0, "amount": 14600.0},
            {"item_code": "STRL-CAR PROTECT KIT (CAR CLEAN SET)", "item_name": "CAR PROTECTION KIT", "qty": 1, "uom": "PC", "rate": 250.0, "amount": 250.0}
        ]
    },
    {
        "company": "Wheel Core",
        "vehicle": "NBC-1234",
        "date": add_days(nowdate(), -3),
        "status": "Completed",
        "services": [
            {"service_item": "WHEEL BALANCING - FREE", "description": "HIGH SPEED WHEEL BALANCING (4 WHEELS)", "hours": 1.0, "rate": 800.0, "amount": 800.0},
            {"service_item": "TIRE MOUNTING/ DISMOUNTING - FREE", "description": "MAGS & TIRE INSTALLATION & NITROGEN INFLATION", "hours": 1.0, "rate": 600.0, "amount": 600.0}
        ],
        "parts": [
            {"item_code": "P2024-08018", "item_name": "XT1885 TE37 XT 18X8.5 6X139.7 ET -10 MAGNESIUM BLUE", "qty": 4, "uom": "PC", "rate": 13750.0, "amount": 55000.0},
            {"item_code": "185/70 R14 YOKOHAMA ES32", "item_name": "265/60 R18 ROADCRUZA RA1100 ALL-TERRAIN TIRE", "qty": 4, "uom": "PC", "rate": 7800.0, "amount": 31200.0}
        ]
    },
    {
        "company": "Ultra MRF Dau Annex",
        "vehicle": "CAL-5678",
        "date": add_days(nowdate(), -5),
        "status": "Invoiced",
        "services": [
            {"service_item": "CHANGE OIL", "description": "FULL SYNTHETIC ENGINE OIL & FILTER SERVICE", "hours": 1.0, "rate": 650.0, "amount": 650.0},
            {"service_item": "PULL OUT BRAKE  CALIPER PIN - DM-VMMS-OS", "description": "BRAKE SYSTEM CLEANING & ROTOR RESURFACING", "hours": 2.0, "rate": 900.0, "amount": 1800.0}
        ],
        "parts": [
            {"item_code": "STRL-CAR PROTECT KIT (CAR CLEAN SET)", "item_name": "MOBIL 1 ADVANCED FULL SYNTHETIC 5W-30 (4L)", "qty": 2, "uom": "PC", "rate": 2850.0, "amount": 5700.0},
            {"item_code": "CKH-5501", "item_name": "CERAMIC BRAKE PADS FRONT SET", "qty": 1, "uom": "SET", "rate": 2450.0, "amount": 2450.0}
        ]
    },
    {
        "company": "Ultra MRF Telebastagan",
        "vehicle": "RKH344",
        "date": add_days(nowdate(), -6),
        "status": "Completed",
        "services": [
            {"service_item": "WHEEL ALIGNMENT (TOE-IN, TOE-OUT)", "description": "COMPUTERIZED 4-WHEEL ALIGNMENT", "hours": 1.0, "rate": 1100.0, "amount": 1100.0},
            {"service_item": "MISCELLANEOUS", "description": "UNDERCHASSIS INSPECTION & SUSPENSION TORQUE", "hours": 1.0, "rate": 450.0, "amount": 450.0}
        ],
        "parts": [
            {"item_code": "185/70 R14 YOKOHAMA ES32", "item_name": "195/65 R15 DUNLOP ENASAVE EC300+", "qty": 4, "uom": "PC", "rate": 3950.0, "amount": 15800.0}
        ]
    },
    {
        "company": "Automan Car Care Center",
        "vehicle": "NBC-1234",
        "date": add_days(nowdate(), -8),
        "status": "Invoiced",
        "services": [
            {"service_item": "PMS LABOR (LIGHT)", "description": "COMPREHENSIVE 50-POINT VEHICLE HEALTH CHECK & PMS", "hours": 2.5, "rate": 900.0, "amount": 2250.0},
            {"service_item": "TROUBLE SHOOTING ELECTRICAL WIRING", "description": "BATTERY & CHARGING SYSTEM DIAGNOSTICS", "hours": 1.0, "rate": 750.0, "amount": 750.0}
        ],
        "parts": [
            {"item_code": "STRL-CAR PROTECT KIT (CAR CLEAN SET)", "item_name": "MOTOLITE GOLD 24SMF AUTOMOTIVE BATTERY", "qty": 1, "uom": "PC", "rate": 5800.0, "amount": 5800.0},
            {"item_code": "STRL-CAR PROTECT KIT (CAR CLEAN SET)", "item_name": "PRESTONE LONG LIFE COOLANT (4L)", "qty": 1, "uom": "PC", "rate": 850.0, "amount": 850.0}
        ]
    },
    {
        "company": "The Wheelhub",
        "vehicle": "CAL-5678",
        "date": add_days(nowdate(), -10),
        "status": "Completed",
        "services": [
            {"service_item": "TIRE MOUNTING/ DISMOUNTING - FREE", "description": "MAGS UPGRADE & TIRE BALANCING PACKAGE", "hours": 2.0, "rate": 850.0, "amount": 1700.0}
        ],
        "parts": [
            {"item_code": "P2024-08023", "item_name": "UL2095 TE37 ULTRA LARGE PCD 20X9.5 6X139.7 ET 0 MAGNESIUM BLUE", "qty": 4, "uom": "PC", "rate": 15000.0, "amount": 60000.0},
            {"item_code": "185/70 R14 YOKOHAMA ES32", "item_name": "265/50 R20 MICHELIN PILOT SPORT 4 SUV TIRE", "qty": 4, "uom": "PC", "rate": 14500.0, "amount": 58000.0}
        ]
    }
]

created_jos = 0
for job in SAMPLE_JOBS:
    jo = frappe.get_doc({
        "doctype": "Vehicle Job Order",
        "company": job["company"],
        "customer": "BENNY DEL ROSARIO",
        "vehicle": job["vehicle"],
        "job_order_date": job["date"],
        "status": job["status"],
        "payment_status": "Paid",
        "services": [{
            "service_item": s["service_item"],
            "description": s["description"],
            "hours": s["hours"],
            "rate": s["rate"],
            "total_amount": s["amount"]
        } for s in job["services"]],
        "parts": [{
            "item_code": p["item_code"],
            "item_name": p["item_name"],
            "qty": p["qty"],
            "uom": p["uom"],
            "rate": p["rate"],
            "amount": p["amount"]
        } for p in job["parts"]]
    })
    jo.insert(ignore_permissions=True)
    created_jos += 1
    print(f"  + Created Job Order {jo.name} for '{job['company']}' (Total: PHP {jo.grand_total:,.2f})")

frappe.db.commit()
print(f"\nSuccessfully populated {created_jos} multi-company transactions!")
