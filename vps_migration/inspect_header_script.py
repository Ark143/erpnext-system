import requests

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

res = session.get(f"{BASE_URL}/api/resource/Client%20Script/VM%20Header%20Shortcut%20Button")
print(res.json().get("data", {}).get("script"))
