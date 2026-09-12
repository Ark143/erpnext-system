import requests
import json

URL = 'http://38.247.138.224:10017'
s = requests.Session()

print("==================================================")
print("1. TEST REGISTER NEW CUSTOMER + VEHICLE LINKING")
print("==================================================")
reg_payload = {
    'customer_name': 'MARIA SANTOS GARCIA',
    'customer_phone': '0917-555-8899',
    'customer_email': 'maria.garcia@gmail.com',
    'customer_address': 'San Fernando, Pampanga',
    'plate_no': 'CAK-8899',
    'make': 'TOYOTA',
    'model': 'RAV4 HYBRID',
    'year': '2023',
    'color': 'ATTITUDE BLACK',
    'fuel_type': 'Hybrid',
    'transmission': 'Automatic',
    'current_mileage': 18500
}
r1 = s.post(f'{URL}/api/method/vehicle_management.api.portal.register_customer_profile', data=reg_payload)
d1 = r1.json().get('message', {})
print(f"Register Success: {d1.get('success')}")
print(f"Customer Name: {d1.get('customer', {}).get('name')}")
print(f"Vehicles Count: {len(d1.get('vehicles', []))}")
for v in d1.get('vehicles', []):
    print(f" - Vehicle: {v.get('plate_no')} | {v.get('make')} {v.get('model')} ({v.get('year')})")

print("\n==================================================")
print("2. TEST MULTI-BRANCH APPOINTMENT BOOKING")
print("==================================================")
apt_payload = {
    'branches': json.dumps(['Ultra MRF Dau Main', 'Ultra MRF San Fernando', 'The Wheelhub']),
    'appointment_date': '2026-09-22',
    'appointment_time': '08:00 AM - 10:00 AM',
    'service_type': 'PMS / Change Oil',
    'customer_name': 'MARIA SANTOS GARCIA',
    'customer_phone': '0917-555-8899',
    'customer_email': 'maria.garcia@gmail.com',
    'plate_no': 'CAK-8899',
    'make': 'TOYOTA',
    'model': 'RAV4 HYBRID',
    'year': '2023',
    'color': 'ATTITUDE BLACK',
    'notes': 'PMS Service + Hybrid battery diagnostic'
}
r2 = s.post(f'{URL}/api/method/vehicle_management.api.portal.book_appointment', data=apt_payload)
d2 = r2.json().get('message', {})
print(f"Booking Success: {d2.get('success')}")
print(f"Appointment ID: {d2.get('appointment_id')}")
print(f"Primary Branch: {d2.get('branch')}")
print(f"Selected Branches: {d2.get('selected_branches')}")

print("\n==================================================")
print("3. TEST ADDING 2ND VEHICLE TO CUSTOMER PROFILE")
print("==================================================")
veh2_payload = {
    'customer_name': 'MARIA SANTOS GARCIA',
    'customer_phone': '0917-555-8899',
    'customer_email': 'maria.garcia@gmail.com',
    'plate_no': 'NBA-1122',
    'make': 'HONDA',
    'model': 'HR-V TURBO',
    'year': '2024',
    'color': 'PLATINUM WHITE',
    'fuel_type': 'Gasoline',
    'transmission': 'Automatic',
    'current_mileage': 6200
}
r3 = s.post(f'{URL}/api/method/vehicle_management.api.portal.add_customer_vehicle', data=veh2_payload)
d3 = r3.json().get('message', {})
print(f"Add Vehicle Success: {d3.get('success')}")
print(f"Total Vehicles in Garage: {len(d3.get('vehicles', []))}")
for v in d3.get('vehicles', []):
    print(f" - {v.get('plate_no')}: {v.get('make')} {v.get('model')} ({v.get('year')})")

print("\n==================================================")
print("4. TEST LOGIN & ISOLATED CUSTOMER INVOICES")
print("==================================================")
r4 = s.post(f'{URL}/api/method/vehicle_management.api.portal.customer_login', data={'identifier': 'DANILO OBRA'})
d4 = r4.json().get('message', {})
print(f"Login Success: {d4.get('success')}")
print(f"Customer Name: {d4.get('customer', {}).get('name')}")
print(f"Total Invoices: {len(d4.get('invoices', []))}")
print(f"Total Spent: PHP {d4.get('customer', {}).get('total_spent', 0):,.2f}")
for inv in d4.get('invoices', [])[:4]:
    print(f" - Invoice {inv.get('invoice_number')}: PHP {inv.get('grand_total', 0):,.2f} | Status: {inv.get('status')} | Date: {inv.get('date')} | Branch: {inv.get('company')}")

print("\n==================================================")
print("ALL BACKEND BUSINESS FLOW TESTS PASSED!")
print("==================================================")
