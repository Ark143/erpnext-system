import urllib.request
import json

base_url = "http://127.0.0.1:8000"

# Test calling executive dashboard API
req = urllib.request.Request(f"{base_url}/api/method/executive_dashboard?view=meta", headers={"Host": "erp.localhost"})
with urllib.request.urlopen(req) as resp:
    print(f"Executive Dashboard Meta Status: {resp.status}")

# Test calling approvals
req2 = urllib.request.Request(f"{base_url}/api/method/executive_dashboard?view=approvals&company=Ultra%20MRF%20Dau%20Main", headers={"Host": "erp.localhost"})
with urllib.request.urlopen(req2) as resp2:
    print(f"Executive Dashboard Approvals Status: {resp2.status}")

print("HTTP Server is live and responding perfectly!")
