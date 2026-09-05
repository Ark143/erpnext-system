import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Check what vm_pos_get_items returns
res = s.get(f'{URL}/api/method/vm_pos_get_items?txt=YOKOHAMA&limit=5').json()
print("vm_pos_get_items response:")
for it in res.get('message', [])[:5]:
    print(" ", it)

# Check Customer Vehicle with 12020 or plate 12020
veh = s.get(f'{URL}/api/resource/Customer Vehicle?filters=[["license_plate","like","%12020%"]]', params={'limit_page_length': 5}).json()
print("\nCustomer Vehicle search license_plate 12020:", veh.get('data'))

veh2 = s.get(f'{URL}/api/resource/Customer Vehicle?filters=[["plate_no","like","%12020%"]]', params={'limit_page_length': 5}).json()
print("Customer Vehicle search plate_no 12020:", veh2.get('data'))

veh3 = s.get(f'{URL}/api/resource/Customer Vehicle?filters=[["name","like","%12020%"]]', params={'limit_page_length': 5}).json()
print("Customer Vehicle search name 12020:", veh3.get('data'))

# Check Customer with 006 GUAJIO
cust = s.get(f'{URL}/api/resource/Customer?filters=[["customer_name","like","%GUAJIO%"]]', params={'limit_page_length': 5}).json()
print("\nCustomer search GUAJIO:", cust.get('data'))
