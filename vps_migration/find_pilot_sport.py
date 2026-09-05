import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

res = s.get(f'{URL}/api/resource/Item Price', params={
    'filters': json.dumps([['price_list_rate', '>=', 21800], ['price_list_rate', '<=', 21900]]),
    'fields': json.dumps(['name', 'item_code', 'price_list_rate', 'item_name'])
}).json()
print("Item Prices ~21862.5:", res.get('data'))

res2 = s.get(f'{URL}/api/resource/Item Price', params={
    'filters': json.dumps([['item_name', 'like', '%PILOT SPORT%']]),
    'fields': json.dumps(['name', 'item_code', 'price_list_rate', 'item_name']),
    'limit_page_length': 20
}).json()
print("\nPilot Sport Item Prices:", res2.get('data'))
