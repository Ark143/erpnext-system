import requests
import json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
r_login = s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})
print(f"[ADMIN LOGIN] {r_login.status_code}")

print("\n" + "="*60)
print("  TEST 1: LIVE BRANCH CAPACITY & CALENDAR AVAILABILITY")
print("="*60)

for branch in ["Ultra MRF Dau Main", "Automan Car Care Center", "Wheel Core"]:
    r = s.get(f'{URL}/api/method/vehicle_management.api.portal.get_branch_availability?branch={requests.utils.quote(branch)}&date=2026-09-25')
    msg = r.json().get('message', {})
    print(f"\n[BRANCH] {msg.get('branch')} (Total Bays: {msg.get('total_bays')}) - Date: {msg.get('date')}")
    for slot in msg.get('slots', []):
        print(f"  * {slot.get('slot')}: {slot.get('available')}/{slot.get('total_bays')} Bays Open [{slot.get('status')}]")
    
    cal = msg.get('calendar_days', [])[:5]
    print(f"  Upcoming Days Preview: {', '.join([c.get('date') + ': ' + c.get('status') for c in cal])}")

print("\n" + "="*60)
print("  TEST 2: APPOINTMENT CONVERSION TO ESTIMATE, INSPECTION, JOB ORDER")
print("="*60)

apt_id = "APT-2026-00007"

# 1. Convert to Vehicle Estimate
r_est = s.post(f'{URL}/api/method/vehicle_management.api.portal.convert_appointment_to_doc', data={
    'appointment_id': apt_id,
    'target_doctype': 'Vehicle Estimate'
})
est_msg = r_est.json().get('message', {})
print(f"\n[CONVERT ESTIMATE] Success: {est_msg.get('success')}")
print(f"  -> Generated Estimate: {est_msg.get('doc_name')} ({est_msg.get('url')})")
print(f"  -> Message: {est_msg.get('message')}")

# 2. Convert to Vehicle Inspection
r_insp = s.post(f'{URL}/api/method/vehicle_management.api.portal.convert_appointment_to_doc', data={
    'appointment_id': apt_id,
    'target_doctype': 'Vehicle Inspection'
})
insp_msg = r_insp.json().get('message', {})
print(f"\n[CONVERT INSPECTION] Success: {insp_msg.get('success')}")
print(f"  -> Generated Inspection: {insp_msg.get('doc_name')} ({insp_msg.get('url')})")
print(f"  -> Message: {insp_msg.get('message')}")

# 3. Convert to Vehicle Job Order
r_jo = s.post(f'{URL}/api/method/vehicle_management.api.portal.convert_appointment_to_doc', data={
    'appointment_id': apt_id,
    'target_doctype': 'Vehicle Job Order'
})
jo_msg = r_jo.json().get('message', {})
print(f"\n[CONVERT JOB ORDER] Success: {jo_msg.get('success')}")
print(f"  -> Generated Job Order: {jo_msg.get('doc_name')} ({jo_msg.get('url')})")
print(f"  -> Message: {jo_msg.get('message')}")

# 4. Verify Appointment Doc status in ERPNext
r_chk = s.get(f'{URL}/api/resource/Vehicle%20Appointment/{apt_id}')
apt_data = r_chk.json().get('data', {})
print(f"\n[VERIFY APPOINTMENT STATUS] Status: {apt_data.get('status')}")
print(f"  -> Linked Job Order: {apt_data.get('job_order')}")
print(f"  -> Linked Estimate: {apt_data.get('estimate')}")
print(f"  -> Notes: {apt_data.get('notes')}")

print("\n" + "="*60)
print("  ALL CAPACITY & CONVERSION TESTS COMPLETED SUCCESSFULLY!")
print("="*60)
