import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Let's call vm_pos_create_invoice
payload = {
    "company": "ULTRA MRF",
    "customer": "Cash Customer", # or check existing customer
    "payment_method": "Cash",
    "paid_amount": 100,
    "items": [{"item_code": "01004", "qty": 1, "rate": 100, "discount_amount": 0, "uom": "Nos"}]
}

# Fetch real customer and item first
custs = s.get(f'{URL}/api/resource/Customer?limit=1').json().get('data', [])
items = s.get(f'{URL}/api/resource/Item?limit=1&filters=[["is_sales_item","=",1]]').json().get('data', [])

if custs and items:
    payload['customer'] = custs[0]['name']
    payload['items'][0]['item_code'] = items[0]['name']
    print(f"Testing with Customer: {payload['customer']}, Item: {payload['items'][0]['item_code']}")

res = s.post(f'{URL}/api/method/vm_pos_create_invoice', json={'data': payload})
print("vm_pos_create_invoice Response Status:", res.status_code)
print("vm_pos_create_invoice Response JSON:", json.dumps(res.json(), indent=2))
