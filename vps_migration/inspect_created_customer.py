import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'})

doc = session.get(f"{BASE_URL}/api/resource/Customer/Ultra%20MRF%20Mexico%20Warehouse").json()
print("Customer 'Ultra MRF Mexico Warehouse':")
print(json.dumps(doc, indent=2))
