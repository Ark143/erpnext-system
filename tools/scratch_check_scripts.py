import requests
import json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# 1. Customer Doc
r_cust = s.get(f'{URL}/api/resource/Customer/ENGR%20JUAN%20DELA%20CRUZ')
print("Customer Doc:", r_cust.json().get('data'))

# 2. Customer Vehicle check
r_cv = s.get(f'{URL}/api/resource/Customer%20Vehicle', params={'filters': json.dumps([['plate_no', 'like', '%NDX%']])})
print("Customer Vehicles matching NDX:", r_cv.json().get('data'))

# 3. Error logs
r_err = s.get(f'{URL}/api/resource/Error%20Log', params={'limit_page_length': 3, 'order_by': 'creation desc'})
for e in r_err.json().get('data', []):
    err = s.get(f'{URL}/api/resource/Error%20Log/{e["name"]}').json().get('data', {})
    print("\n--- ERROR LOG ---", err.get('name'))
    print(err.get('error')[:600] if err.get('error') else 'Empty')
