import requests

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

res = session.get(f"{BASE_URL}/api/resource/Client Script?fields=[\"name\",\"dt\",\"enabled\"]&limit_page_length=50")
print("Existing Client Scripts:")
for cs in res.json().get("data", []):
    print(f" - {cs['name']} on {cs['dt']}")
