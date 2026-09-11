import requests, json

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=15)

# Inspect Financial Reports
fr_ws = session.get(f"{BASE_URL}/api/resource/Workspace/Financial%20Reports").json().get('data', {})
print("Financial Reports title:", fr_ws.get('title'))
print("Financial Reports shortcuts:", [s.get('label') or s.get('shortcut_name') for s in fr_ws.get('shortcuts', [])])
print("Financial Reports links/cards:", [c.get('label') for c in fr_ws.get('links', [])])

# Inspect Vehicle Management
vm_ws = session.get(f"{BASE_URL}/api/resource/Workspace/Vehicle%20Management").json().get('data', {})
print("\nVehicle Management shortcuts:", [s.get('label') or s.get('shortcut_name') for s in vm_ws.get('shortcuts', [])])
