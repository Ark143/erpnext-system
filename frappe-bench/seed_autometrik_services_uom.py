"""
Seed Autometrik Services, Service Groups, Service Categories, and UOMs into ERPNext.

Run from frappe-bench/sites:
    ..\env\Scripts\python.exe ..\seed_autometrik_services_uom.py

Steps:
  1. Add UOMs from Autometrik  (UOM doctype)
  2. Add service groups as Item Groups under "Services" parent
  3. Add service categories as Item Group sub-nodes under their group
  4. Import services as Items (is_stock_item=0, item_type=Service)
"""

import sys
import os
import json
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))

import frappe

frappe.init("site1.local")
frappe.connect()

AUTOMETRIK_BASE = "https://app.autometrik.ph"
AUTOMETRIK_COOKIES = r"C:\Users\josem\.gemini\autometrik_cookies.txt"


# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────

def load_cookies():
    """Read cookies from curl cookie jar file."""
    cookies = {}
    if not os.path.exists(AUTOMETRIK_COOKIES):
        return cookies
    with open(AUTOMETRIK_COOKIES) as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 7:
                cookies[parts[5]] = parts[6]
    return cookies


def autometrik_login():
    """Login to Autometrik and return session."""
    session = requests.Session()
    resp = session.post(
        f"{AUTOMETRIK_BASE}/account/signin",
        data={"Username": "apacson", "Password": "Cyndi0816!", "RememberMe": "false", "ReturnUrl": ""},
        allow_redirects=True,
    )
    return session


# ─────────────────────────────────────────────────────────
# 1. UOMs from Autometrik
# ─────────────────────────────────────────────────────────

AUTOMETRIK_UOMS = [
    {"abbr": "PC",   "name": "PIECE"},
    {"abbr": "SET",  "name": "SET"},
    {"abbr": "LITER","name": "LITER"},
    {"abbr": "GAL",  "name": "GALLON"},
    {"abbr": "L",    "name": "L"},
    {"abbr": "ML",   "name": "ML"},
    {"abbr": "PML",  "name": "PML"},
    {"abbr": "S",    "name": "S"},
    {"abbr": "GAL ", "name": "GAL"},
    {"abbr": "DRUM", "name": "DRUM"},
]


def seed_uoms():
    print("\n=== Seeding UOMs ===")
    created = 0
    skipped = 0
    for uom in AUTOMETRIK_UOMS:
        name = uom["name"].strip()
        if frappe.db.exists("UOM", name):
            print(f"  SKIP UOM: {name}")
            skipped += 1
            continue
        doc = frappe.get_doc({
            "doctype": "UOM",
            "uom_name": name,
            "must_be_whole_number": 0,
            "enabled": 1,
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"  CREATED UOM: {name}")
        created += 1
    print(f"UOMs: {created} created, {skipped} skipped")


# ─────────────────────────────────────────────────────────
# 2. Item Groups (Service Groups & Categories)
# ─────────────────────────────────────────────────────────

SERVICE_GROUPS = [
    "GENERAL REPAIRS",
    "OTHER SERVICES",
    "PROMOTIONS",
    "QUICK SERVICES",
    "SUBLET",
    "TIRE / WHEEL SERVICES",
]

SERVICE_CATEGORIES = [
    {"category": "BODY EXTERIOR",                                     "description": "Body exterior repair and paint services."},
    {"category": "BODY INTERIOR",                                     "description": "Interior trim, upholstery, and cabin services."},
    {"category": "BRAKE SYSTEM",                                      "description": "Brake pads, discs, calipers, and hydraulic brake services."},
    {"category": "CHASSIS/ AXLE",                                     "description": "Suspension arms, bearings, joints, stabilizers, and differential assemblies."},
    {"category": "COOLING SYSTEM",                                    "description": "Radiator, coolant flush, thermostat, and water pump services."},
    {"category": "DIAGNOSTICS & INSPECTION",                          "description": "Vehicle diagnostics, computer scanning, and inspection services."},
    {"category": "ELECTRICAL SYSTEM",                                 "description": "Wiring, battery, alternator, starter, and electrical component services."},
    {"category": "ENGINE",                                            "description": "Engine overhaul, timing belt, gasket, and internal engine services."},
    {"category": "EXHAUST SYSTEM",                                    "description": "Muffler, catalytic converter, exhaust pipe, and emission services."},
    {"category": "FUEL SYSTEM",                                       "description": "Fuel injector cleaning, fuel pump, and fuel filter services."},
    {"category": "HEATER, VENTILLATION / AIR CONDITIONING (HVAC)",    "description": "A/C recharge, compressor, heater core, and cabin air services."},
    {"category": "OTHERS",                                            "description": "Miscellaneous automotive services not in other categories."},
    {"category": "PREVENTIVE MAINTENANCE",                            "description": "Oil change, filter replacement, and scheduled maintenance services."},
    {"category": "STEERING SYSTEM",                                   "description": "Power steering, rack and pinion, tie rod, and alignment services."},
    {"category": "TIRES/ WHEELS",                                     "description": "Tire mounting, balancing, rotation, and wheel alignment services."},
    {"category": "TRANSMISSION",                                      "description": "Transmission flush, clutch, gearbox, and drivetrain services."},
]


def ensure_item_group(name, parent, is_group=0, description=None):
    """Create item group if it doesn't exist; return the name."""
    if frappe.db.exists("Item Group", name):
        return name
    doc = frappe.get_doc({
        "doctype": "Item Group",
        "item_group_name": name,
        "parent_item_group": parent,
        "is_group": is_group,
        "description": description or "",
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print(f"  CREATED Item Group: {name}  (parent={parent})")
    return name


def seed_item_groups():
    print("\n=== Seeding Item Groups (Service Groups) ===")

    # Ensure top-level "Services" group exists
    ensure_item_group("Services", "All Item Groups", is_group=1,
                      description="All automotive service items")

    # Create each service group under "Services"
    for grp in SERVICE_GROUPS:
        ensure_item_group(grp, "Services", is_group=1,
                          description=f"{grp} - automotive service group")

    print("\n=== Seeding Item Groups (Service Categories) ===")
    # Categories go under the matching group where possible,
    # else under "Services" (they're cross-group in Autometrik)
    for cat_info in SERVICE_CATEGORIES:
        cat = cat_info["category"]
        desc = cat_info["description"]
        # Normalize: "DIAGNOSTICS & INSPECTION" might have HTML entity in source
        ensure_item_group(cat, "Services", is_group=0, description=desc)


# ─────────────────────────────────────────────────────────
# 3. Import Services as Items
# ─────────────────────────────────────────────────────────

def seed_services(session):
    print("\n=== Fetching services from Autometrik ===")
    resp = session.post(
        f"{AUTOMETRIK_BASE}/service/getdata",
        data={
            "draw": "1",
            "start": "0",
            "length": "10000",
            "search[value]": "",
            "order[0][column]": "0",
            "order[0][dir]": "asc",
        },
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    data = resp.json()
    services = data.get("data", [])
    total = data.get("recordsTotal", 0)
    print(f"  Total services from Autometrik: {total}, fetched: {len(services)}")

    created = 0
    skipped = 0
    errors = []

    for svc in services:
        name = (svc.get("Name") or "").strip()
        if not name:
            continue

        code = (svc.get("Code") or "").strip() or name[:140]
        group_name = (svc.get("GroupName") or "").strip() or "OTHER SERVICES"
        category_name = (svc.get("CategoryName") or "").strip()
        rate = float(svc.get("ServiceAmount") or 0)
        std_hours = float(svc.get("StandardHour") or 1)

        # Item group: use category if it exists, else group
        item_group = category_name if (category_name and frappe.db.exists("Item Group", category_name)) else group_name
        if not frappe.db.exists("Item Group", item_group):
            item_group = "Services"

        # Check for duplicate by item_code
        if frappe.db.exists("Item", {"item_code": code}):
            skipped += 1
            continue

        # Also check by name match (prevent near-duplicate service names)
        # Use item_code = code, item_name = name
        try:
            doc = frappe.get_doc({
                "doctype": "Item",
                "item_code": code[:140],
                "item_name": name[:140],
                "item_group": item_group,
                "is_stock_item": 0,
                "stock_uom": "Nos",
                "is_purchase_item": 0,
                "is_sales_item": 1,
                "include_item_in_manufacturing": 0,
                "description": name,
                "standard_rate": rate,
                # Custom fields if they exist
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            created += 1
            if created % 50 == 0:
                print(f"  Progress: {created} services created...")
        except Exception as e:
            err_msg = str(e)
            errors.append({"name": name, "code": code, "error": err_msg})
            if len(errors) <= 5:
                print(f"  ERROR creating '{name}': {err_msg[:120]}")

    print(f"\nServices: {created} created, {skipped} skipped, {len(errors)} errors")
    if errors:
        print(f"  First errors: {errors[:3]}")

    return created, skipped, errors


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────

def main():
    print("=== Autometrik Services & UOM Import ===\n")

    # Step 1: UOMs
    seed_uoms()

    # Step 2: Item Groups
    seed_item_groups()

    # Step 3: Services
    print("\nLogging in to Autometrik...")
    session = autometrik_login()
    # Verify login
    test = session.get(f"{AUTOMETRIK_BASE}/service")
    if "Sign in" in test.text and "signin" in test.url:
        print("ERROR: Could not log in to Autometrik. Check credentials.")
        sys.exit(1)
    print("Login successful.")

    created, skipped, errors = seed_services(session)

    print("\n=== Summary ===")
    print(f"  Services created : {created}")
    print(f"  Services skipped : {skipped}")
    print(f"  Services errored : {len(errors)}")
    print("\nDone!")


if __name__ == "__main__":
    main()
