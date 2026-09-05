import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

res = s.get(f'{URL}/api/resource/Item', params={
    'filters': json.dumps([['name', 'like', '%MICHELIN%']]),
    'limit_page_length': 100
}).json()
print("Michelin items:")
for it in res.get('data', []):
    if '265' in it['name'] or 'PILOT' in it['name'] or '18' in it['name']:
        print(" ", it['name'])

res2 = s.get(f'{URL}/api/resource/Item', params={
    'filters': json.dumps([['name', 'like', '%265/65%']]),
    'limit_page_length': 100
}).json()
print("\n265/65 items:")
for it in res2.get('data', []):
    print(" ", it['name'])
