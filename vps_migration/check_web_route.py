import requests

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

res = session.get(f"{BASE_URL}/consolidated_financials")
print("Web route /consolidated_financials status:", res.status_code)
if res.status_code == 200:
    print("Page title / snippet:", res.text[:300])
else:
    print("Response text:", res.text[:300])
