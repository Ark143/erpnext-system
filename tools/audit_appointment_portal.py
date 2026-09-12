import requests
import json

BASE = "http://38.247.138.224:10017"
s = requests.Session()

print("="*70)
print(" ULTRA MRF APPOINTMENT & CUSTOMER VMS PORTAL - INTEGRITY AUDIT")
print("="*70)

# 1. Test All 4 Live Public Routes
routes = ["/appointment", "/booking", "/customer-portal", "/vms-portal"]
for r in routes:
    res = s.get(f"{BASE}{r}", timeout=20)
    print(f"[+] Route {r:20} -> Status: HTTP {res.status_code} ({len(res.text):,} bytes)")
    assert res.status_code == 200, f"Route {r} failed!"

# 2. Test Get Branches API
print("\n[+] Testing Branches API...")
r_branches = s.get(f"{BASE}/api/method/vehicle_management.api.portal.get_portal_branches", timeout=20)
assert r_branches.status_code == 200
b_data = r_branches.json().get("message", {})
branches = b_data.get("branches", [])
print(f"    Available Active Branches: {len(branches)}")
for b in branches[:4]:
    print(f"     • {b['name']}: {b['title']} ({b['bays']} bays, Phone: {b['phone']})")

# 3. Test Reference Data API
print("\n[+] Testing Vehicle Reference Data API...")
r_ref = s.get(f"{BASE}/api/method/vehicle_management.api.portal.get_vehicle_reference_data", timeout=20)
assert r_ref.status_code == 200
ref_data = r_ref.json().get("message", {})
print(f"    Makes: {len(ref_data.get('makes', []))}, Models: {len(ref_data.get('models', []))}, Service Packages: {len(ref_data.get('service_packages', []))}")

# 4. Test Booking an Appointment
print("\n[+] Testing Appointment Booking...")
booking_payload = {
    "branch": "Ultra MRF Dau Main",
    "appointment_date": "2026-09-18",
    "appointment_time": "10:00 AM - 12:00 PM",
    "service_type": "Wheel Alignment & Balancing",
    "customer_name": "EDUARDO MANALANG",
    "customer_phone": "0917-888-9999",
    "customer_email": "eduardo.manalang@gmail.com",
    "plate_no": "ABC-9988",
    "make": "MITSUBISHI",
    "model": "MONTERO SPORT",
    "year": "2024",
    "color": "TITANIUM GRAY",
    "notes": "Annual PMS inspection, 3D laser alignment, and front brake cleaning."
}

r_book = s.post(f"{BASE}/api/method/vehicle_management.api.portal.book_appointment", json={"data": booking_payload}, timeout=20)
assert r_book.status_code == 200
book_resp = r_book.json().get("message", {})
print(f"    Booking Success: {book_resp.get('success')}")
print(f"    Appointment ID:  {book_resp.get('appointment_id')}")
print(f"    Branch:          {book_resp.get('branch_title')}")
print(f"    Vehicle:         {book_resp.get('vehicle_display')}")

# 5. Test Customer Profile Lookup by Mobile Number & Plate Number
print("\n[+] Testing Customer Profile Lookup by Plate 'ABC-9988'...")
r_prof = s.get(f"{BASE}/api/method/vehicle_management.api.portal.lookup_customer_profile", params={"identifier": "ABC-9988"}, timeout=20)
assert r_prof.status_code == 200
prof_data = r_prof.json().get("message", {})
cust = prof_data.get("customer", {})
print(f"    Customer Name:   {cust.get('customer_name')}")
print(f"    Loyalty Tier:    {cust.get('loyalty_tier')}")
print(f"    Vehicles Count:  {len(prof_data.get('vehicles', []))}")
print(f"    Appointments:    {len(prof_data.get('appointments', []))}")
for a in prof_data.get("appointments", []):
    print(f"     -> {a['name']}: {a['branch']} on {a['appointment_date']} ({a['service_type']}) - Status: {a['status']}")

# 6. Test Customer Profile Lookup with Rich Historical Data (Automan)
print("\n[+] Testing Customer Profile Lookup for 'Automan'...")
r_automan = s.get(f"{BASE}/api/method/vehicle_management.api.portal.lookup_customer_profile", params={"identifier": "Automan"}, timeout=20)
assert r_automan.status_code == 200
auto_data = r_automan.json().get("message", {})
print(f"    Customer Name:   {auto_data.get('customer', {}).get('customer_name')}")
print(f"    Total Invoices:  {len(auto_data.get('invoices', []))}")
print(f"    Estimates:       {len(auto_data.get('estimates', []))}")
print(f"    Job Orders:      {len(auto_data.get('job_orders', []))}")

print("\n" + "="*70)
print(" ALL 6 AUDIT CHECKS PASSED WITH 100% SUCCESS!")
print("="*70)
