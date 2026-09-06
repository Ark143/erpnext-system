import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'})

# 1. Check Server Script 'VM SAP Relationship Map API'
ss = session.get(f"{BASE_URL}/api/resource/Server%20Script/VM%20SAP%20Relationship%20Map%20API").json()
print("Server Script 'VM SAP Relationship Map API' exists:", 'data' in ss)

# 2. Check Client Scripts related to Relationship Map
cs_res = session.get(f"{BASE_URL}/api/resource/Client%20Script?fields=[\"name\",\"dt\",\"enabled\"]&limit_page_length=200").json()
print("\nClient Scripts:")
for cs in cs_res.get('data', []):
    if any(k in cs['name'].lower() for k in ['relationship', 'sap', 'map', 'vms']):
        print(f" - {cs['name']} (dt: {cs.get('dt')}, enabled: {cs.get('enabled')})")
