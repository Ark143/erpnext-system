import requests
import json

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f'{BASE_URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

logs = session.get(f'{BASE_URL}/api/resource/Error%20Log?limit_page_length=5&order_by=creation%20desc&fields=["name","method","error"]').json().get('data', [])
for l in logs:
    print(f"\n--- Error Log: {l.get('name')} | Method: {l.get('method')} ---")
    print(l.get('error'))
