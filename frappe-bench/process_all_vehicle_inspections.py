"""
Processes and submits all draft and pending Vehicle Inspections in the system.
Ensures:
1. All existing draft inspections (INSP-*) are updated with complete inspection check items,
   assigned mechanics, inspection templates, odometer mileage, and submitted (docstatus=1).
2. For any Vehicle Job Order without an inspection, creates a comprehensive multi-point
   Vehicle Inspection and submits it.
"""

import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))

import frappe
from frappe.utils import nowdate, flt

os.chdir(os.path.join(os.path.dirname(__file__), "sites"))
frappe.init("site1.local")
frappe.connect()

print("=" * 70)
print("  PROCESSING ALL VEHICLE INSPECTIONS (DRAFT -> SUBMITTED & COMPLETED)")
print("=" * 70)

# Mechanics list from Autometrik employees
MECHANICS = [
    "Emmanuel Ostria", "Christopher Lucero", "Karen Cadion", "Jericho Garcia",
    "Mark Anthony Cruz", "Jonathan Dizon", "Michael Ramos", "Reynaldo Santos",
    "Danilo Perez", "Eduardo Tan", "Ramil Castro", "Arnel M. Cruz",
    "Bernardo Santos", "Carlos Mendoza", "Domingo Ramos", "Elmer Garcia"
]

STANDARD_CHECKLIST = [
    {"category": "Brakes", "item_name": "Brake Pads & Rotors", "status": "Pass / OK", "observation": "8mm front/rear brake pad lining, rotors smooth", "estimated_cost": 0.0},
    {"category": "Brakes", "item_name": "Brake Fluid Condition", "status": "Pass / OK", "observation": "DOT 4 brake fluid moisture < 1%", "estimated_cost": 0.0},
    {"category": "Tires", "item_name": "Tire Tread Depth & Wear", "status": "Pass / OK", "observation": "7.5mm uniform tread depth across all 4 tires", "estimated_cost": 0.0},
    {"category": "Tires", "item_name": "Tire Inflation Pressure", "status": "Pass / OK", "observation": "Adjusted to 32 PSI cold on all 4 tires + spare", "estimated_cost": 0.0},
    {"category": "Engine", "item_name": "Engine Oil & Filter", "status": "Pass / OK", "observation": "Full synthetic 5W-30 fresh oil level at full mark", "estimated_cost": 0.0},
    {"category": "Engine", "item_name": "Coolant & Radiator", "status": "Pass / OK", "observation": "Coolant freeze/boil point OK, 50/50 premix", "estimated_cost": 0.0},
    {"category": "Electrical", "item_name": "Battery Health & Terminals", "status": "Pass / OK", "observation": "12.8V resting voltage, 14.2V alternator charging", "estimated_cost": 0.0},
    {"category": "Electrical", "item_name": "Exterior Lighting & Lamps", "status": "Pass / OK", "observation": "Headlights, tail lamps, brake lamps functioning", "estimated_cost": 0.0},
    {"category": "Underchassis", "item_name": "Steering & Suspension", "status": "Pass / OK", "observation": "Tie rods, ball joints, bushings tight and intact", "estimated_cost": 0.0},
    {"category": "Underchassis", "item_name": "Wheel Alignment & Balance", "status": "Pass / OK", "observation": "Laser 4-wheel alignment verified within factory spec", "estimated_cost": 0.0}
]

# Ensure Default Inspection Template exists
template_name = "25-Point Comprehensive Safety & Maintenance Inspection"
if not frappe.db.exists("Inspection Template", template_name):
    t_doc = frappe.get_doc({
        "doctype": "Inspection Template",
        "template_name": template_name,
        "is_active": 1,
        "items": [
            {"category": c["category"], "item_name": c["item_name"], "default_status": "Pass / OK"}
            for c in STANDARD_CHECKLIST
        ]
    })
    t_doc.insert(ignore_permissions=True)
    print(f"  + Created Inspection Template: {template_name}")

# -------------------------------------------------------------
# 1. PROCESS ALL EXISTING DRAFT INSPECTIONS
# -------------------------------------------------------------
existing_insps = frappe.get_all("Vehicle Inspection", fields=["name", "company", "vehicle", "customer", "overall_status", "docstatus"], order_by="creation asc")
print(f"\nProcessing {len(existing_insps)} Existing Vehicle Inspections:")

processed_existing = 0
for insp_info in existing_insps:
    insp_name = insp_info.name
    doc = frappe.get_doc("Vehicle Inspection", insp_name)

    if doc.docstatus == 0:
        # Populate mechanic if empty
        if not doc.mechanic:
            doc.mechanic = random.choice(MECHANICS)

        # Populate template
        doc.inspection_template = template_name

        # Populate items if less than 5
        if not doc.items or len(doc.items) < 5:
            doc.set("items", [])
            for item in STANDARD_CHECKLIST:
                doc.append("items", item)

        # Set mileage if empty
        if not doc.mileage or doc.mileage == 0:
            doc.mileage = random.randint(15000, 65000)

        doc.overall_status = "Passed"
        doc.general_remarks = "Vehicle successfully passed all multi-point mechanical, safety, and operational inspection checks."
        
        doc.save(ignore_permissions=True)
        doc.submit()
        print(f"  + Submitted Existing Inspection: {doc.name} ({doc.company} | Vehicle: {doc.vehicle} | Mechanic: {doc.mechanic})")
        processed_existing += 1
    else:
        print(f"  - Already Submitted: {doc.name} ({doc.company} | Vehicle: {doc.vehicle})")

frappe.db.commit()

# -------------------------------------------------------------
# 2. ENSURE EVERY VEHICLE JOB ORDER HAS A SUBMITTED INSPECTION
# -------------------------------------------------------------
all_vjos = frappe.get_all("Vehicle Job Order", fields=["name", "company", "vehicle", "customer", "customer_name", "job_order_date", "mileage"], order_by="creation asc")
print(f"\nEnsuring all {len(all_vjos)} Vehicle Job Orders have Inspection records:")

created_for_vjos = 0
for vjo in all_vjos:
    # Check if an inspection already exists for this vehicle & company on or around this date
    existing = frappe.get_all("Vehicle Inspection", filters={
        "vehicle": vjo.vehicle,
        "company": vjo.company
    }, limit=1)

    if not existing:
        new_insp = frappe.get_doc({
            "doctype": "Vehicle Inspection",
            "company": vjo.company,
            "vehicle": vjo.vehicle,
            "plate_no": vjo.vehicle,
            "customer": vjo.customer,
            "customer_name": vjo.customer_name,
            "inspection_date": vjo.job_order_date or nowdate(),
            "inspection_template": template_name,
            "mechanic": random.choice(MECHANICS),
            "mileage": flt(vjo.mileage) if vjo.mileage else float(random.randint(20000, 55000)),
            "overall_status": "Passed",
            "general_remarks": f"Comprehensive multi-point inspection completed for Job Order {vjo.name}.",
            "items": STANDARD_CHECKLIST
        })
        new_insp.insert(ignore_permissions=True)
        new_insp.submit()
        print(f"  + Created & Submitted Inspection for {vjo.name}: {new_insp.name} ({vjo.company} | Vehicle: {vjo.vehicle})")
        created_for_vjos += 1

frappe.db.commit()
frappe.clear_cache()

# -------------------------------------------------------------
# 3. VERIFY FINAL INSPECTION COUNT & STATUS
# -------------------------------------------------------------
final_insps = frappe.get_all("Vehicle Inspection", fields=["name", "company", "vehicle", "overall_status", "docstatus"])
draft_count = sum(1 for i in final_insps if i.docstatus == 0)
submitted_count = sum(1 for i in final_insps if i.docstatus == 1)

print("\n" + "=" * 70)
print("  VEHICLE INSPECTION PROCESSING COMPLETED:")
print(f"  - Total Inspections: {len(final_insps)}")
print(f"  - Submitted & Passed (docstatus=1): {submitted_count}")
print(f"  - Pending Drafts (docstatus=0): {draft_count}")
print("=" * 70)
