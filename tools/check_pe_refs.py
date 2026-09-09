import requests
import json

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'})

# Check Payment Entries
pe1 = session.get(f"{BASE_URL}/api/resource/Payment%20Entry/ACC-PAY-2026-00234").json().get('data', {})
print("PE Pay References:", pe1.get('references'))

pe2 = session.get(f"{BASE_URL}/api/resource/Payment%20Entry/ACC-PAY-2026-00235").json().get('data', {})
print("PE Receive References:", pe2.get('references'))

# Check invoices
si = session.get(f"{BASE_URL}/api/resource/Sales%20Invoice/ACC-SINV-2026-00416").json().get('data', {})
print("SI Outstanding:", si.get('outstanding_amount'), "Status:", si.get('status'))

pi = session.get(f"{BASE_URL}/api/resource/Purchase%20Invoice/ACC-PINV-2026-00182").json().get('data', {})
print("PI Outstanding:", pi.get('outstanding_amount'), "Status:", pi.get('status'))
