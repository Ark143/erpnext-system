import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Let's inspect the error in lookup_customer_profile
r = s.get(f'{URL}/api/resource/Error%20Log?order_by=creation%20desc&limit_page_length=3')
for e in r.json().get('data', []):
    err = s.get(f'{URL}/api/resource/Error%20Log/{e["name"]}').json().get('data', {})
    print("Error Log:", err.get('name'), err.get('error')[:300] if err.get('error') else '')
