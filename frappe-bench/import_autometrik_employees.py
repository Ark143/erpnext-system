"""
Import all 187 scraped Autometrik employees into ERPNext Employee records.
"""

import sys, os, re, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))

import frappe
from frappe.utils import getdate

os.chdir(os.path.join(os.path.dirname(__file__), "sites"))
frappe.init("site1.local")
frappe.connect()

print("=" * 65)
print("  IMPORTING AUTOMETRIK EMPLOYEES INTO ERPNEXT")
print("=" * 65)

# Load scratchpad JSON
scratchpad_path = r"C:\Users\josem\.gemini\antigravity-ide\brain\ce890146-6655-40b5-a9cf-3c59f7bedae1\browser\scratchpad_xavjkff9.md"
with open(scratchpad_path, "r", encoding="utf-8") as f:
    content = f.read()

json_match = re.search(r"```json\s*(\[[\s\S]*?\])\s*```", content)
if not json_match:
    raise ValueError("Could not find JSON array in scratchpad!")

employees_data = json.loads(json_match.group(1))
print(f"Total employees extracted from scratchpad: {len(employees_data)}")

# Map Locations to Company and Branch
COMPANY_MAP = {
    "Ultra MRF Dau Main": "Ultra MRF Dau Main",
    "Ultra MRF Dau Annex": "Ultra MRF Dau Annex",
    "Ultra MRF San Fernando": "Ultra MRF San Fernando",
    "Wheel Core": "Wheel Core",
    "San Fernando Warehouse": "San Fernando Warehouse",
    "ULTRA MRF MEXICO WAREHOUSE": "Ultra MRF Mexico Warehouse",
    "Ultra MRF Mexico Warehouse": "Ultra MRF Mexico Warehouse",
    "Ultra MRF Telebastagan": "Ultra MRF Telebastagan",
    "Ultra MRF Telebastagan 2": "Ultra MRF Telebastagan 2",
    "Ultra MRF Warehouse Dau": "Ultra MRF Warehouse Dau",
    "AUTOMAN CAR CARE CENTER": "Automan Car Care Center",
    "Automan Car Care Center": "Automan Car Care Center",
    "THE WHEELHUB": "The Wheelhub",
    "The Wheelhub": "The Wheelhub",
}

BRANCH_MAP = {
    "Ultra MRF Dau Main": "Ultra MRF Dau Main",
    "Ultra MRF Dau Annex": "Ultra MRF Dau Annex",
    "Ultra MRF San Fernando": "Ultra MRF San Fernando",
    "Wheel Core": "Wheel Core",
    "San Fernando Warehouse": "San Fernando Warehouse",
    "ULTRA MRF MEXICO WAREHOUSE": "Ultra MRF Mexico Warehouse",
    "Ultra MRF Mexico Warehouse": "Ultra MRF Mexico Warehouse",
    "Ultra MRF Telebastagan": "Ultra MRF Telebastagan",
    "Ultra MRF Telebastagan 2": "Ultra MRF Telebastagan 2",
    "Ultra MRF Warehouse Dau": "Ultra MRF Warehouse Dau",
    "AUTOMAN CAR CARE CENTER": "Automan Car Care Center",
    "Automan Car Care Center": "Automan Car Care Center",
    "THE WHEELHUB": "The Wheelhub",
    "The Wheelhub": "The Wheelhub",
}

# Designation normalization map
DESIGNATION_MAP = {
    "TECHNICIAN": "Technician",
    "TIREMAN": "Tireman",
    "SERVICE ADVISOR": "Service Advisor",
    "SALES REPRESENTATIVE": "Sales Representative",
    "BRANCH HEAD": "Branch Head",
    "ADMIN CASHIER": "Admin Cashier",
    "WAREHOUSEMEN": "Warehouseman",
    "DRIVER": "Driver",
    "PROCUREMENT HEAD OFFICER": "Procurement Head Officer",
    "AUDITOR": "Auditor",
    "ACCOUNTING": "Accountant",
    "MECHANIC": "Technician",
    "HELPER": "Technician Helper",
    "OFFICE STAFF": "Administrative Assistant"
}

def ensure_designation(designation_name):
    norm = DESIGNATION_MAP.get(designation_name.upper().strip(), designation_name.title().strip())
    if not norm:
        norm = "Technician"
    if not frappe.db.exists("Designation", norm):
        doc = frappe.get_doc({
            "doctype": "Designation",
            "designation_name": norm
        })
        doc.insert(ignore_permissions=True)
        print(f"  + Created Designation: {norm}")
    return norm

def parse_date(date_str):
    if not date_str:
        return None
    date_str = date_str.strip()
    try:
        # MM-DD-YYYY
        parts = date_str.split("-")
        if len(parts) == 3:
            if len(parts[2]) == 4: # MM-DD-YYYY
                return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            elif len(parts[0]) == 4: # YYYY-MM-DD
                return date_str
    except Exception:
        pass
    return None

created_count = 0
updated_count = 0

for emp in employees_data:
    raw_name = emp.get("name", "").strip()
    if not raw_name:
        continue

    # Split name into first and last
    name_parts = re.sub(r"\s+", " ", raw_name).split(" ")
    if len(name_parts) == 1:
        first_name = name_parts[0].title()
        last_name = ""
    else:
        first_name = " ".join(name_parts[:-1]).title()
        last_name = name_parts[-1].title()

    full_name = f"{first_name} {last_name}".strip()

    raw_desig = emp.get("designation", "").strip() or "Technician"
    designation = ensure_designation(raw_desig)

    loc = emp.get("location", "").strip()
    company = COMPANY_MAP.get(loc, "ULTRA MRF")
    branch = BRANCH_MAP.get(loc, None)

    # Check if company exists in DB
    if not frappe.db.exists("Company", company):
        company = "ULTRA MRF"

    # Check if branch exists in DB
    if branch and not frappe.db.exists("Branch", branch):
        b_doc = frappe.get_doc({"doctype": "Branch", "branch": branch})
        b_doc.insert(ignore_permissions=True)

    mobile = emp.get("mobileNo", "").strip()
    date_of_joining = parse_date(emp.get("date", ""))
    emp_no = emp.get("employeeNo", "").strip()

    # Check if employee already exists by name and company
    existing = frappe.db.get_value(
        "Employee",
        {"first_name": first_name, "last_name": last_name, "company": company},
        "name"
    ) or frappe.db.get_value(
        "Employee",
        {"employee_name": full_name, "company": company},
        "name"
    )

    if existing:
        emp_doc = frappe.get_doc("Employee", existing)
        emp_doc.designation = designation
        if branch:
            emp_doc.branch = branch
        if mobile and not emp_doc.cell_number:
            emp_doc.cell_number = mobile
            emp_doc.custom_mobile_no = mobile
        if date_of_joining and not emp_doc.date_of_joining:
            emp_doc.date_of_joining = date_of_joining
        emp_doc.status = "Active"
        emp_doc.save(ignore_permissions=True)
        updated_count += 1
    else:
        emp_doc = frappe.get_doc({
            "doctype": "Employee",
            "first_name": first_name,
            "last_name": last_name,
            "employee_name": full_name,
            "gender": "Other",
            "date_of_birth": "1995-01-01",
            "date_of_joining": date_of_joining or "2025-01-01",
            "company": company,
            "branch": branch,
            "designation": designation,
            "status": "Active",
            "cell_number": mobile,
            "custom_mobile_no": mobile,
            "employment_type": "Full-time"
        })
        emp_doc.insert(ignore_permissions=True)
        created_count += 1

frappe.db.commit()
frappe.clear_cache()

print("\n" + "=" * 65)
print(f"  SUCCESSFULLY IMPORTED EMPLOYEES:")
print(f"  - Newly Created: {created_count}")
print(f"  - Updated: {updated_count}")
print(f"  - Total Processed: {created_count + updated_count}")
print("=" * 65)
