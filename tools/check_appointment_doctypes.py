import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

r = s.get(f'{URL}/api/resource/DocType', params={'filters': json.dumps([['name', 'like', '%Appointment%']])})
print("Appointment DocTypes:", r.json())

# Check Event and ToDo
r2 = s.get(f'{URL}/api/resource/DocType', params={'filters': json.dumps([['name', 'in', ['Event', 'ToDo', 'Customer Vehicle', 'Vehicle Job Order', 'Vehicle Estimate', 'Vehicle Service Reminder']]])})
print("Related DocTypes:", [d['name'] for d in r2.json().get('data', [])])
