import requests

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

res = session.get(f"{BASE_URL}/api/resource/Item?limit_page_length=500&fields=[\"name\",\"item_name\",\"item_group\",\"stock_uom\"]")
data = res.json().get("data", [])
print(f"Total items in tabItem: {len(data)}")
