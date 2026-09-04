import requests
import json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=15)

# Read the server script from deploy_complete_sap_relationship_map.py
import re
with open('c:/Users/josem/erpnext-system/vps_migration/deploy_complete_sap_relationship_map.py', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'server_script_code = """(.*?)"""\s*server_script_payload', content, re.DOTALL)
if not match:
    print("Could not find server script code")
    exit(1)

script_code = match.group(1)

res = s.put('http://38.247.138.224:10017/api/resource/Server Script/VM SAP Relationship Map API', json={
    'script': script_code,
    'disabled': 0
}, timeout=15)
print("Updated Server Script:", res.status_code)

# Now test ACC-SINV-2026-00166
res_test = s.get('http://38.247.138.224:10017/api/method/vm_relationship_map', params={
    'doctype': 'Sales Invoice',
    'docname': 'ACC-SINV-2026-00166'
}, timeout=15)

data = res_test.json().get('message', {})
print("\n=== SUMMARY for ACC-SINV-2026-00166 ===")
print(json.dumps(data.get('summary', {}), indent=2))
print("\n=== NODES ===")
for n in data.get('nodes', []):
    print(f"  {n.get('doctype')}: {n.get('name')} | Grand: {n.get('grand_total')} | Paid: {n.get('paid_amount')} | Outst: {n.get('outstanding_amount')} | Status: {n.get('status')}")
