import requests

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

res = session.get(f"{BASE_URL}/api/resource/Stock%20Ledger%20Entry?limit_page_length=5")
print("Sample SLEs:", res.json())

# Check total items in tabItem
item_res = session.get(f"{BASE_URL}/api/resource/Item?limit_page_length=10&fields=[\"name\",\"item_name\",\"item_group\",\"stock_uom\"]")
print("Sample Items:", item_res.json())
