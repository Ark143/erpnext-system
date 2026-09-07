import requests, json

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

res = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=pnl&from_date=2026-01-01&to_date=2026-12-31")
print("Status:", res.status_code)
print("Response text:", res.text[:1000])
