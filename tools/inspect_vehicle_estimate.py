import requests
import json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

r = s.get(f'{URL}/api/resource/DocType/Vehicle Estimate')
data = r.json().get('data', {})
fields = data.get('fields', [])
print('=== Vehicle Estimate Fields ===')
for f in fields:
    print(f"{f.get('idx')}: {f.get('fieldname')} ({f.get('fieldtype')}) - {f.get('label')} -> options: {f.get('options')}")

# Check Sales Taxes and Charges DocType
r_tax = s.get(f'{URL}/api/resource/DocType/Sales Taxes and Charges')
print('\nSales Taxes and Charges DocType exists:', r_tax.status_code == 200)
if r_tax.status_code == 200:
    t_fields = [f.get('fieldname') for f in r_tax.json().get('data',{}).get('fields',[])]
    print('Taxes fields:', t_fields)
