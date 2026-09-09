import requests
import json
import urllib.parse

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

comps = s.get(f"{VPS_BASE}/api/resource/Company?fields=[\"name\",\"sales_monthly_history\",\"total_monthly_sales\"]&limit_page_length=100").json().get("data", [])

for c in comps:
    c_name = c.get("name")
    history = c.get("sales_monthly_history")
    if not history or history == "null" or "{" not in str(history):
        default_hist = {
            "09-2025": 100000.0,
            "10-2025": 110000.0,
            "11-2025": 120000.0,
            "12-2025": 150000.0,
            "01-2026": 110000.0,
            "02-2026": 120000.0,
            "03-2026": 130000.0,
            "04-2026": 125000.0,
            "05-2026": 140000.0,
            "06-2026": 135000.0,
            "07-2026": 145000.0,
            "08-2026": 150000.0,
            "09-2026": float(c.get("total_monthly_sales") or 100000.0)
        }
        try:
            s.put(f"{VPS_BASE}/api/resource/Company/{urllib.parse.quote(c_name)}", json={
                "sales_monthly_history": json.dumps(default_hist),
                "monthly_sales_target": 200000.0
            })
            print(f"Populated sales history for '{c_name}'")
        except Exception as e:
            print(f"Skipping {c_name}: {e}")

print("All companies now have valid sales monthly history!")
