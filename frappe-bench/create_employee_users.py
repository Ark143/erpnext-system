"""
Create User accounts for all Employees and link employee.user_id = user.name.
"""

import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))

import frappe
from frappe.utils.password import update_password

os.chdir(os.path.join(os.path.dirname(__file__), "sites"))
frappe.init("site1.local")
frappe.connect()
frappe.flags.in_import = True

print("=" * 65)
print("  CREATING USER ACCOUNTS FOR ALL EMPLOYEES")
print("=" * 65)

DEFAULT_PASSWORD = "UltraMRF@2026!"
DOMAIN = "ultramrf.ph"

def clean_string(s):
    if not s:
        return ""
    # remove non alphanumeric
    return re.sub(r"[^a-zA-Z0-9]", "", s).lower()

def generate_email(first_name, last_name, emp_name, used_emails):
    f = clean_string(first_name)
    l = clean_string(last_name)
    
    if f and l:
        base = f"{f}.{l}"
    elif f:
        base = f
    elif l:
        base = l
    else:
        base = clean_string(emp_name) or "user"
        
    email = f"{base}@{DOMAIN}"
    counter = 1
    while email in used_emails or frappe.db.exists("User", email):
        counter += 1
        email = f"{base}{counter}@{DOMAIN}"
        
    used_emails.add(email)
    return email

def get_roles_for_designation(designation):
    d = (designation or "").lower()
    base_roles = ["Desk User", "Employee"]
    
    if any(k in d for k in ["technician", "tireman", "mechanic", "helper"]):
        return base_roles + ["Maintenance User", "Stock User"]
    elif "service advisor" in d:
        return base_roles + ["Sales User", "Maintenance User", "Stock User"]
    elif any(k in d for k in ["branch head", "owner", "manager", "managing"]):
        return base_roles + ["Sales Manager", "Maintenance Manager", "Stock Manager", "Accounts User"]
    elif any(k in d for k in ["cashier", "accounting", "accountant", "finance"]):
        return base_roles + ["Accounts User", "Sales User"]
    elif any(k in d for k in ["procurement", "purchas"]):
        return base_roles + ["Purchase User", "Stock User"]
    elif any(k in d for k in ["warehouse", "inventory", "stock"]):
        return base_roles + ["Stock User"]
    elif "sales" in d or "representative" in d or "csr" in d or "customer service" in d:
        return base_roles + ["Sales User"]
    elif "driver" in d or "delivery" in d:
        return base_roles + ["Delivery User"]
    else:
        return base_roles + ["Stock User"]

employees = frappe.get_all("Employee", fields=["name", "first_name", "last_name", "employee_name", "designation", "user_id", "cell_number", "company_email", "personal_email"])

used_emails = set([u.name.lower() for u in frappe.get_all("User", fields=["name"])])
created_count = 0
linked_count = 0

for emp in employees:
    # If already linked to an existing user, skip
    if emp.user_id and frappe.db.exists("User", emp.user_id):
        continue

    # Determine email
    email = emp.company_email or emp.personal_email
    if not email or not frappe.db.exists("User", email):
        email = generate_email(emp.first_name, emp.last_name, emp.employee_name, used_emails)

    roles = get_roles_for_designation(emp.designation)
    
    if not frappe.db.exists("User", email):
        user_doc = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": emp.first_name or emp.employee_name,
            "last_name": emp.last_name or "",
            "full_name": emp.employee_name,
            "phone": emp.cell_number,
            "send_welcome_email": 0,
            "user_type": "System User",
            "enabled": 1,
            "roles": [{"role": r} for r in roles]
        })
        user_doc.insert(ignore_permissions=True)
        update_password(user=email, pwd=DEFAULT_PASSWORD)
        created_count += 1
    else:
        user_doc = frappe.get_doc("User", email)
        # Ensure enabled and roles
        for r in roles:
            if not any(ur.role == r for ur in user_doc.roles):
                user_doc.append("roles", {"role": r})
        user_doc.enabled = 1
        user_doc.save(ignore_permissions=True)

    # Link to Employee
    frappe.db.set_value("Employee", emp.name, {
        "user_id": email,
        "company_email": email
    }, update_modified=False)
    linked_count += 1

frappe.db.commit()
frappe.clear_cache()

print("\n" + "=" * 65)
print(f"  SUCCESSFULLY CONFIGURED USER ACCOUNTS:")
print(f"  - Users Created: {created_count}")
print(f"  - Employees Linked: {linked_count}")
print(f"  - Default Password for all: {DEFAULT_PASSWORD}")
print("=" * 65)
