import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Let's test with customer 006 GUAJIO, vehicle 12020
payload = {
    "customer": "006 GUAJIO",
    "vehicle": "12020",
    "company": "ULTRA MRF",
    "payment_method": "Cash",
    "paid_amount": 27000,
    "items": [
        {"item_code": "185/70 R14 YOKOHAMA E70J", "qty": 1, "rate": 4500, "uom": "PC"},
        {"item_code": "265/65 R18 MICHELIN PILOT SPO...", "qty": 1, "rate": 21862.50, "uom": "PC"}
    ]
}

# Check if vehicle 12020 and customer 006 GUAJIO exist
veh = s.get(f'{URL}/api/resource/Customer Vehicle/12020').json()
print("Vehicle 12020:", veh.get('data', {}).get('name'), "Customer:", veh.get('data', {}).get('customer'))

# Find real item codes for YOKOHAMA and MICHELIN
items = s.get(f'{URL}/api/resource/Item?filters=[["item_name","like","%YOKOHAMA%"]]', params={'limit_page_length': 5}).json()
print("Yokohama items:", items.get('data'))

res = s.post(f'{URL}/api/method/vm_pos_create_invoice', json={'data': payload})
print("vm_pos_create_invoice Response Status:", res.status_code)
print("vm_pos_create_invoice Response JSON:", json.dumps(res.json(), indent=2))
