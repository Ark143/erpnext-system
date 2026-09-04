import requests
import json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

pe_doc = s.get('http://38.247.138.224:10017/api/resource/Payment Entry/ACC-PAY-2026-00222', timeout=30).json().get('data', {})
print("Payment Entry doc:")
print(f"  name: {pe_doc.get('name')}")
print(f"  docstatus: {pe_doc.get('docstatus')}")
print(f"  paid_amount: {pe_doc.get('paid_amount')}")
print(f"  received_amount: {pe_doc.get('received_amount')}")
print(f"  total_allocated_amount: {pe_doc.get('total_allocated_amount')}")
print(f"  unallocated_amount: {pe_doc.get('unallocated_amount')}")
print(f"  references: {json.dumps(pe_doc.get('references', []), indent=2)}")
