import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Fetch VM POS Items API Server Script
ss = s.get(f'{URL}/api/resource/Server%20Script/VM%20POS%20Items%20API').json()
print("VM POS Items API Script:")
print(ss.get('data', {}).get('script'))
