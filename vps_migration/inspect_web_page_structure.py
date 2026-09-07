import requests

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

res = session.get(f"{BASE_URL}/api/resource/Web Page/vm-dashboard")
doc = res.json().get("data", {})
print("Web Page Doc Keys:", list(doc.keys()))
print("title:", doc.get("title"))
print("route:", doc.get("route"))
print("content_type:", doc.get("content_type"))
print("main_section length:", len(doc.get("main_section") or ""))
