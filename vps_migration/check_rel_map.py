import requests
import json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=10)

# Check Sales Invoice doc itself
si_doc = s.get('http://38.247.138.224:10017/api/resource/Sales Invoice/ACC-SINV-2026-00166', timeout=10).json().get('data', {})
print("Sales Invoice doc fields:")
print(f"  outstanding_amount: {si_doc.get('outstanding_amount')}")
print(f"  grand_total: {si_doc.get('grand_total')}")
print(f"  status: {si_doc.get('status')}")
print(f"  docstatus: {si_doc.get('docstatus')}")

# Query relationship map for ACC-SINV-2026-00166
res = s.get('http://38.247.138.224:10017/api/method/vm_relationship_map', params={
    'doctype': 'Sales Invoice',
    'docname': 'ACC-SINV-2026-00166'
}, timeout=10)

data = res.json().get('message', {})
print("\nSUMMARY:")
print(json.dumps(data.get('summary', {}), indent=2))
print("\nNODES:")
for n in data.get('nodes', []):
    print(f"  {n.get('doctype')}: {n.get('name')} | Grand: {n.get('grand_total')} | Paid: {n.get('paid_amount')} | Outstanding: {n.get('outstanding_amount')} | Status: {n.get('status')}")

print("\nEDGES:")
for e in data.get('edges', []):
    print(f"  {e.get('from')} -> {e.get('to')} ({e.get('label')})")
