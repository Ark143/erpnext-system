import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

fyears = s.get(f"{VPS_BASE}/api/resource/Fiscal Year?fields=[\"name\",\"year\",\"year_start_date\",\"year_end_date\",\"disabled\"]&limit_page_length=50").json().get("data", [])
print("Fiscal Years on VPS:")
print(json.dumps(fyears, indent=2))
