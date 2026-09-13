import requests
import json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
r_login = s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})
print(f"[LOGIN] {r_login.status_code}")

# Read local updated JSON
with open('frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/doctype/vehicle_estimate/vehicle_estimate.json', 'r', encoding='utf-8') as f:
    local_doctype_data = json.load(f)

# Fetch current DocType from VPS
r_get = s.get(f'{URL}/api/resource/DocType/Vehicle%20Estimate')
if r_get.status_code != 200:
    print(f"[ERROR] Could not fetch Vehicle Estimate DocType: {r_get.text}")
    exit(1)

doc = r_get.json().get('data', {})
current_fieldnames = [f.get('fieldname') for f in doc.get('fields', [])]
print(f"Current fields in DocType ({len(current_fieldnames)}):", current_fieldnames)

# Update fields in DocType
new_fields = local_doctype_data.get('fields', [])
doc['fields'] = new_fields

# Save updated DocType
r_put = s.put(f'{URL}/api/resource/DocType/Vehicle%20Estimate', json={'fields': new_fields})
print(f"[UPDATE DOCTYPE] Status: {r_put.status_code}")
if r_put.status_code != 200:
    print("Response:", r_put.text)

# Clear cache
s.post(f'{URL}/api/method/frappe.handler.clear_cache')
print("[OK] Cache cleared.")

# Verify fields
r_verify = s.get(f'{URL}/api/resource/DocType/Vehicle%20Estimate')
v_fields = [f.get('fieldname') for f in r_verify.json().get('data', {}).get('fields', [])]
print(f"Verified fields in Vehicle Estimate ({len(v_fields)}):")
for fn in ['sec_taxes', 'taxes_and_charges', 'taxes', 'total_taxes_and_charges']:
    print(f"  • {fn} -> Present: {fn in v_fields}")
