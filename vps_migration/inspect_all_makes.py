import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# 1. Fetch Vehicle Makes via resource API directly
res_makes = s.get(f'{URL}/api/resource/Vehicle%20Make?fields=["name","make_name"]&limit_page_length=500')
makes = res_makes.json().get('data', [])

print(f"Total Vehicle Makes: {len(makes)}")
for m in makes:
    print(m)
