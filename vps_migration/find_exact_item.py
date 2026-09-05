import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Search Item Price with price between 21860 and 21865
res = s.get(f'{URL}/api/resource/Item Price', params={
    'filters': json.dumps([['price_list_rate', '>=', 21862], ['price_list_rate', '<=', 21863]]),
    'fields': json.dumps(['name', 'item_code', 'price_list_rate', 'item_name'])
}).json()
print("Exact Item Price for 21862.50:", res.get('data'))

# Search Item with standard_rate between 21860 and 21865
res_item = s.get(f'{URL}/api/resource/Item', params={
    'filters': json.dumps([['standard_rate', '>=', 21862], ['standard_rate', '<=', 21863]]),
    'fields': json.dumps(['name', 'item_name', 'standard_rate'])
}).json()
print("Exact Item with rate 21862.50:", res_item.get('data'))
