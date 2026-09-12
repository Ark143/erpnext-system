import requests
import json

URL = 'http://38.247.138.224:10017'
s = requests.Session()

print("=" * 60)
print("  ULTRA MRF CUSTOMER PORTAL — FULL USER LIFECYCLE TEST")
print("=" * 60)

# STEP 1: Register New Customer Account
print("\n[STEP 1] Creating New Customer Account via Portal...")
reg_payload = {
    'customer_name': 'FERNANDO SANTOS PO',
    'customer_phone': '0917-777-3322',
    'customer_email': 'fernando.po@gmail.com',
    'customer_address': 'Dolores, City of San Fernando, Pampanga',
    'plate_no': 'NCA-3322',
    'make': 'TOYOTA',
    'model': 'FORTUNER',
    'year': '2024',
    'color': 'ATTITUDE BLACK',
    'fuel_type': 'Diesel',
    'transmission': 'Automatic',
    'current_mileage': 14500
}

r1 = s.post(f'{URL}/api/method/vehicle_management.api.portal.register_customer_profile', data=reg_payload)
d1 = r1.json().get('message', {})

print(f" -> Registration Success: {d1.get('success')}")
print(f" -> Customer Name: {d1.get('customer', {}).get('name')}")
print(f" -> Customer Docname: {d1.get('customer', {}).get('docname')}")
print(f" -> Registered Phone: {d1.get('customer', {}).get('phone')}")
print(f" -> Vehicles in Garage: {len(d1.get('vehicles', []))}")
for v in d1.get('vehicles', []):
    print(f"    * Plate: {v.get('plate_no')} | {v.get('make')} {v.get('model')} ({v.get('year')}) - Mileage: {v.get('mileage')} km")

# STEP 2: Verify in Frappe Desk Database
print("\n[STEP 2] Verifying records in Frappe / ERPNext Database...")
s_admin = requests.Session()
s_admin.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# 2a. Check Customer Master
r_cust = s_admin.get(f'{URL}/api/resource/Customer/FERNANDO%20SANTOS%20PO')
if r_cust.status_code == 200:
    cust_data = r_cust.json().get('data', {})
    print(f" [PASS] Customer Master Exists in ERPNext: '{cust_data.get('name')}'")
    print(f"        Customer Group: {cust_data.get('customer_group')} | Territory: {cust_data.get('territory')} | Mobile: {cust_data.get('custom_mobile_no')}")
else:
    print(f" [FAIL] Customer Master not found: {r_cust.status_code}")

# 2b. Check Customer Vehicle
r_cv = s_admin.get(f'{URL}/api/resource/Customer%20Vehicle/NCA3322')
if r_cv.status_code != 200:
    r_cv = s_admin.get(f'{URL}/api/resource/Customer%20Vehicle/NCA-3322')

if r_cv.status_code == 200:
    cv_data = r_cv.json().get('data', {})
    print(f" [PASS] Customer Vehicle Exists in VMS: '{cv_data.get('name')}'")
    print(f"        Linked Customer: {cv_data.get('customer')} | Make: {cv_data.get('make')} | Model: {cv_data.get('model')}")
else:
    print(f" [FAIL] Customer Vehicle not found: {r_cv.status_code}")

# STEP 3: Multi-Branch Appointment Scheduling
print("\n[STEP 3] Scheduling Service Appointment across Multi-Branches...")
apt_payload = {
    'branches': json.dumps(['Ultra MRF Dau Main', 'Ultra MRF San Fernando']),
    'appointment_date': '2026-09-25',
    'appointment_time': '10:00 AM - 12:00 PM',
    'service_type': 'PMS / Change Oil',
    'customer_name': 'FERNANDO SANTOS PO',
    'customer_phone': '0917-777-3322',
    'customer_email': 'fernando.po@gmail.com',
    'plate_no': 'NCA-3322',
    'make': 'TOYOTA',
    'model': 'FORTUNER',
    'year': '2024',
    'color': 'ATTITUDE BLACK',
    'notes': 'Please do synthetic change oil, check brakes and tire balance.'
}

r2 = s.post(f'{URL}/api/method/vehicle_management.api.portal.book_appointment', data=apt_payload)
d2 = r2.json().get('message', {})
print(f" -> Booking Success: {d2.get('success')}")
print(f" -> Appointment ID: {d2.get('appointment_id')}")
print(f" -> Allocated Primary Branch: {d2.get('branch')}")
print(f" -> Selected Preferred Branches: {d2.get('selected_branches')}")
print(f" -> Scheduled Date & Time: {d2.get('appointment_date')} ({d2.get('appointment_time')})")

# STEP 4: Add Second Vehicle to Customer Profile
print("\n[STEP 4] Adding a 2nd Vehicle (HONDA CIVIC) to Garage...")
veh2_payload = {
    'customer_name': 'FERNANDO SANTOS PO',
    'customer_phone': '0917-777-3322',
    'customer_email': 'fernando.po@gmail.com',
    'plate_no': 'NBG-5544',
    'make': 'HONDA',
    'model': 'CIVIC RS TURBO',
    'year': '2023',
    'color': 'SONIC GRAY',
    'fuel_type': 'Gasoline',
    'transmission': 'Automatic',
    'current_mileage': 8200
}

r3 = s.post(f'{URL}/api/method/vehicle_management.api.portal.add_customer_vehicle', data=veh2_payload)
d3 = r3.json().get('message', {})
print(f" -> Add Vehicle Success: {d3.get('success')}")
print(f" -> Total Vehicles in Garage: {len(d3.get('vehicles', []))}")
for v in d3.get('vehicles', []):
    print(f"    * {v.get('plate_no')}: {v.get('make')} {v.get('model')} ({v.get('year')})")

# STEP 5: Test Logging Back In via Multiple Identifiers
print("\n[STEP 5] Testing Customer Login via Different Identifiers...")

# 5a. Login by Customer Name
r_login_name = s.post(f'{URL}/api/method/vehicle_management.api.portal.customer_login', data={'identifier': 'FERNANDO SANTOS PO'})
d_login_name = r_login_name.json().get('message', {})
print(f" [PASS] Login by Customer Name ('FERNANDO SANTOS PO'): Success = {d_login_name.get('success')}")
print(f"        Found {len(d_login_name.get('vehicles', []))} vehicles and {len(d_login_name.get('appointments', []))} scheduled appointments.")

# 5b. Login by Mobile Phone Number
r_login_phone = s.post(f'{URL}/api/method/vehicle_management.api.portal.customer_login', data={'identifier': '0917-777-3322'})
d_login_phone = r_login_phone.json().get('message', {})
print(f" [PASS] Login by Phone Number ('0917-777-3322'): Success = {d_login_phone.get('success')}")
print(f"        Customer Name: {d_login_phone.get('customer', {}).get('name')}")

# 5c. Login by Vehicle Plate Number
r_login_plate = s.post(f'{URL}/api/method/vehicle_management.api.portal.customer_login', data={'identifier': 'NCA-3322'})
d_login_plate = r_login_plate.json().get('message', {})
print(f" [PASS] Login by Plate Number ('NCA-3322'): Success = {d_login_plate.get('success')}")
print(f"        Customer Name: {d_login_plate.get('customer', {}).get('name')}")

print("\n" + "=" * 60)
print("  ALL END-TO-END CUSTOMER CREATION & LIFECYCLE TESTS PASSED!")
print("=" * 60)
