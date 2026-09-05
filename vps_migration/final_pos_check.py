import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

print("--- 1. Testing vm_pos_get_shift ---")
shift = s.get(f'{URL}/api/method/vm_pos_get_shift?company=ULTRA+MRF').json()
print("Shift Status:", shift.get('message'))

print("\n--- 2. Testing vm_pos_create_invoice ---")
cust = s.get(f'{URL}/api/resource/Customer?limit=1').json().get('data', [])[0]['name']
item = s.get(f'{URL}/api/resource/Item?limit=1&filters=[["is_sales_item","=",1]]').json().get('data', [])[0]['name']
veh = s.get(f'{URL}/api/resource/Customer Vehicle?limit=1').json().get('data', [])[0]['name']

inv_res = s.post(f'{URL}/api/method/vm_pos_create_invoice', json={
    'data': {
        'company': 'ULTRA MRF',
        'customer': cust,
        'vehicle': veh,
        'payment_method': 'Cash',
        'paid_amount': 350,
        'items': [{'item_code': item, 'qty': 1, 'rate': 350, 'uom': 'Nos'}],
        'remarks': 'Test transaction automated check'
    }
}).json()
print("Created Invoice:", inv_res.get('message'))

print("\n--- 3. Testing vm_pos_history ---")
hist = s.get(f'{URL}/api/method/vm_pos_history?company=ULTRA+MRF&period=all').json()
recent = (hist.get('message') or [])[:3]
for r in recent:
    print(f"  {r.get('name')} | {r.get('customer_name')} | PHP {r.get('total_amount')} | {r.get('status')} | Vehicle: {r.get('vehicle')}")
