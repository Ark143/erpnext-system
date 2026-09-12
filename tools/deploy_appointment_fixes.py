#!/usr/bin/env python3
"""
Fix the VM Portal Book Appointment server script - remove all import statements
as Frappe's RestrictedPython blocks __import__.
"""
import requests
import urllib.parse

URL = 'http://38.247.138.224:10017'
s = requests.Session()
r = s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})
print(f"[LOGIN] {r.status_code}: {r.json().get('message')}")
csrf = s.cookies.get('csrf_token', 'fetch')

# NOTE: Frappe Server Scripts CANNOT use "import" - frappe is pre-injected as a global.
# Use frappe.parse_json() instead of json.loads()
# Use frappe.db.exists() instead of os.path.exists()
# DO NOT use: import frappe, import json, import os, etc.

BOOK_APPOINTMENT_SCRIPT = '''
BRANCH_METADATA = {
    "Ultra MRF Dau Main": {"title": "ULTRA MRF Dau Main Branch", "address": "MacArthur Highway, Dau, Mabalacat City, Pampanga", "phone": "(045) 892-1234 / 0917-555-0101"},
    "Ultra MRF Dau Annex": {"title": "ULTRA MRF Dau Annex Branch", "address": "Dau Access Road, Mabalacat City, Pampanga", "phone": "(045) 892-5678 / 0917-555-0102"},
    "Ultra MRF San Fernando": {"title": "ULTRA MRF San Fernando Branch", "address": "Jose Abad Santos Ave (OG Road), San Fernando, Pampanga", "phone": "(045) 961-4321 / 0917-555-0201"},
    "Ultra MRF Telebastagan": {"title": "ULTRA MRF Telebastagan Branch", "address": "MacArthur Highway, Telebastagan, City of San Fernando, Pampanga", "phone": "(045) 436-7890 / 0917-555-0301"},
    "Ultra MRF Telebastagan 2": {"title": "ULTRA MRF Telebastagan 2 Express", "address": "Commercial Complex, Telebastagan, Pampanga", "phone": "(045) 436-7892 / 0917-555-0302"},
    "Automan Car Care Center": {"title": "Automan Car Care Center", "address": "Lazatin Blvd, Dolores, City of San Fernando, Pampanga", "phone": "(045) 963-8888 / 0917-555-0401"},
    "Wheel Core": {"title": "Wheel Core Custom & Tire Depot", "address": "Sindalan Commercial Corridor, San Fernando, Pampanga", "phone": "(045) 961-9999 / 0917-555-0501"},
    "The Wheelhub": {"title": "The Wheelhub Auto Concept", "address": "Clark Perimeter Road, Angeles City, Pampanga", "phone": "(045) 625-1111 / 0917-555-0601"},
    "ULTRA MRF": {"title": "ULTRA MRF Central Operations", "address": "Pampanga Main Commercial Hub", "phone": "(045) 892-0000 / 0917-555-0000"},
}

SERVICE_TYPE_MAP = {
    "PMS / Change Oil": "PMS / Change Oil",
    "Tires & Wheels": "Tires & Wheels",
    "Wheel Alignment": "Wheel Alignment & Balancing",
    "Wheel Alignment & Balancing": "Wheel Alignment & Balancing",
    "Brakes": "Brake System Service",
    "Brake System Service": "Brake System Service",
    "Underchassis": "Underchassis & Suspension",
    "Underchassis & Suspension": "Underchassis & Suspension",
    "Car Aircon": "Car Aircon Service",
    "Car Aircon Service": "Car Aircon Service",
    "Engine Diagnostics": "Engine Diagnostics & Tune-up",
    "Engine Diagnostics & Tune-up": "Engine Diagnostics & Tune-up",
    "Car Wash & Detailing": "Car Wash & Detailing",
    "Battery & Electrical": "Battery & Electrical",
    "General Mechanical Repair": "General Mechanical Repair",
}

raw_data = frappe.form_dict.get("data") or frappe.form_dict
if isinstance(raw_data, str):
    try:
        raw_data = frappe.parse_json(raw_data)
    except Exception:
        raw_data = {}

if isinstance(raw_data, dict) and "data" in raw_data and isinstance(raw_data.get("data"), dict):
    raw_data = raw_data["data"]

branch = raw_data.get("branch") or "Ultra MRF Dau Main"
apt_date = raw_data.get("appointment_date")
apt_time = raw_data.get("appointment_time") or "08:00 AM - 10:00 AM"
raw_service = raw_data.get("service_type") or "PMS / Change Oil"
service_type = SERVICE_TYPE_MAP.get(raw_service, "PMS / Change Oil")

cust_name = str(raw_data.get("customer_name") or "").strip().upper()
phone = str(raw_data.get("customer_phone") or "").strip()
email = str(raw_data.get("customer_email") or "").strip()
plate_no = str(raw_data.get("plate_no") or "").strip().upper()
make = str(raw_data.get("make") or "").strip().upper()
model_input = str(raw_data.get("model") or "").strip().upper()
year = str(raw_data.get("year") or "").strip()
color = str(raw_data.get("color") or "").strip().upper()
notes = str(raw_data.get("notes") or "").strip()

if not cust_name or not phone or not plate_no or not apt_date:
    frappe.response["message"] = {"success": False, "error": "Missing required fields: Customer Name, Phone, Plate No, and Date are required."}
else:
    # Ensure Vehicle Make exists
    if make and not frappe.db.exists("Vehicle Make", make):
        try:
            frappe.get_doc({"doctype": "Vehicle Make", "name": make, "make_name": make}).insert(ignore_permissions=True)
        except Exception:
            pass

    # Ensure Vehicle Model exists
    model_docname = None
    if make and model_input:
        if frappe.db.exists("Vehicle Model", model_input):
            model_docname = model_input
        else:
            combined = make + "-" + model_input
            if frappe.db.exists("Vehicle Model", combined):
                model_docname = combined
            else:
                found = frappe.db.get_value("Vehicle Model", {"model_name": model_input, "make": make}, "name")
                if found:
                    model_docname = found
                else:
                    try:
                        vm = frappe.get_doc({
                            "doctype": "Vehicle Model",
                            "make": make,
                            "model_name": model_input,
                            "category": "Sedan"
                        })
                        vm.insert(ignore_permissions=True)
                        model_docname = vm.name
                    except Exception:
                        model_docname = None

    # Resolve or Create Customer
    customer_docname = None
    existing_cust = frappe.get_all("Customer", filters={"customer_name": cust_name}, pluck="name", limit=1)
    if not existing_cust and phone:
        existing_cust = frappe.get_all("Customer", filters={"mobile_no": phone}, pluck="name", limit=1)

    if existing_cust:
        customer_docname = existing_cust[0]
        if phone:
            frappe.db.set_value("Customer", customer_docname, "mobile_no", phone, update_modified=False)
        if email:
            frappe.db.set_value("Customer", customer_docname, "email_id", email, update_modified=False)
    else:
        try:
            new_c = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": cust_name,
                "customer_type": "Individual",
                "customer_group": "Individual",
                "territory": "All Territories",
                "mobile_no": phone,
                "email_id": email
            })
            new_c.insert(ignore_permissions=True)
            customer_docname = new_c.name
        except Exception:
            customer_docname = None

    # Resolve or Create Vehicle
    vehicle_docname = None
    existing_veh = frappe.get_all("Customer Vehicle", filters={"plate_no": plate_no}, pluck="name", limit=1)
    if existing_veh:
        vehicle_docname = existing_veh[0]
        try:
            update_veh = {"customer": customer_docname or "Cash Customer", "color": color}
            if make:
                update_veh["make"] = make
            if model_docname:
                update_veh["model"] = model_docname
            if year:
                update_veh["year_model"] = year
            frappe.db.set_value("Customer Vehicle", vehicle_docname, update_veh, update_modified=False)
        except Exception:
            pass
    else:
        try:
            veh_data = {
                "doctype": "Customer Vehicle",
                "plate_no": plate_no,
                "customer": customer_docname or "Cash Customer",
                "color": color
            }
            if make:
                veh_data["make"] = make
            if model_docname:
                veh_data["model"] = model_docname
            if year:
                veh_data["year_model"] = year
            new_v = frappe.get_doc(veh_data)
            new_v.insert(ignore_permissions=True)
            vehicle_docname = new_v.name
        except Exception:
            vehicle_docname = None

    # Create Appointment
    try:
        apt_data = {
            "doctype": "Vehicle Appointment",
            "naming_series": "APT-.YYYY.-.#####",
            "branch": branch,
            "appointment_date": apt_date,
            "appointment_time": apt_time,
            "status": "Confirmed",
            "customer_name": cust_name,
            "customer_phone": phone,
            "customer_email": email,
            "plate_no": plate_no,
            "service_type": service_type,
            "notes": notes
        }
        if customer_docname and frappe.db.exists("Customer", customer_docname):
            apt_data["customer"] = customer_docname
        if vehicle_docname:
            apt_data["vehicle"] = vehicle_docname
        if make:
            apt_data["make"] = make
        if model_docname:
            apt_data["model"] = model_docname

        apt_doc = frappe.get_doc(apt_data)
        apt_doc.insert(ignore_permissions=True)

        branch_info = BRANCH_METADATA.get(branch, {})
        vehicle_display = (make + " " + model_input + " (" + plate_no + ")").strip() if (make or model_input) else plate_no

        frappe.response["message"] = {
            "success": True,
            "appointment_id": apt_doc.name,
            "branch": branch,
            "branch_title": branch_info.get("title", branch),
            "branch_address": branch_info.get("address", ""),
            "branch_phone": branch_info.get("phone", ""),
            "appointment_date": apt_date,
            "appointment_time": apt_time,
            "service_type": service_type,
            "customer_name": cust_name,
            "plate_no": plate_no,
            "vehicle_display": vehicle_display,
            "message": "Appointment " + apt_doc.name + " booked for " + cust_name + " at " + branch + " on " + apt_date + "."
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "book_appointment_error")
        frappe.response["message"] = {"success": False, "error": str(e)}
'''

# Update the server script
script_name = "VM Portal Book Appointment"
chk = s.get(f'{URL}/api/resource/Server%20Script/{urllib.parse.quote(script_name)}')
print(f"[CHECK] {script_name}: {chk.status_code}")

if chk.status_code == 200:
    r = s.put(
        f'{URL}/api/resource/Server%20Script/{urllib.parse.quote(script_name)}',
        headers={"X-Frappe-CSRF-Token": csrf},
        json={"script": BOOK_APPOINTMENT_SCRIPT, "disabled": 0, "allow_guest": 1}
    )
    print(f"[UPDATE] {r.status_code}")
    if r.status_code == 200:
        print("[OK] Server script updated - no import statements, uses frappe builtins only")
    else:
        print(f"[FAIL] {r.text[:300]}")
else:
    r = s.post(
        f'{URL}/api/resource/Server Script',
        headers={"X-Frappe-CSRF-Token": csrf},
        json={
            "doctype": "Server Script", "name": script_name,
            "script_type": "API",
            "api_method": "vehicle_management.api.portal.book_appointment",
            "allow_guest": 1, "enabled": 1,
            "script": BOOK_APPOINTMENT_SCRIPT
        }
    )
    print(f"[CREATE] {r.status_code}")

print("\nDone! Now testing the API...")

# Quick API test
import time
time.sleep(1)

test_payload = {
    "branch": "Ultra MRF Dau Main",
    "appointment_date": "2026-09-25",
    "appointment_time": "08:00 AM - 10:00 AM",
    "service_type": "PMS / Change Oil",
    "customer_name": "JOSE TEST DEPLOY",
    "customer_phone": "09177654321",
    "customer_email": "test@ultramrf.ph",
    "plate_no": "ZZZ 8888",
    "make": "TOYOTA",
    "model": "VIOS",
    "year": "2021",
    "color": "BLACK",
    "notes": "Deployment test"
}

r = s.post(
    f'{URL}/api/method/vehicle_management.api.portal.book_appointment',
    headers={'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': csrf},
    json={'data': test_payload}
)
print(f"Test API: {r.status_code}")
resp = r.json()
msg = resp.get('message', resp)
if isinstance(msg, dict):
    print(f"  success: {msg.get('success')}")
    print(f"  appointment_id: {msg.get('appointment_id')}")
    if not msg.get('success'):
        print(f"  error: {msg.get('error')}")
        print(f"  full: {str(resp)[:400]}")
else:
    print(f"  response: {str(resp)[:400]}")
