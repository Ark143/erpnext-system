import requests, json

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

res = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=general_ledger&from_date=2026-01-01&to_date=2026-12-31&page_length=5")
print("Status:", res.status_code)
try:
    exc = json.loads(res.json().get("exc", "[]"))
    print("Full traceback:")
    for line in exc:
        print(line)
except Exception as e:
    print(res.text)
