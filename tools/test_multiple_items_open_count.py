import requests
import json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

items_to_test = ['SRV-ELEC-CHECK', 'PMS', 'PMS-OIL', 'TE37-18X8.5-BRONZE', 'OIL-SYNTHETIC-5W40']

for item_code in items_to_test:
    r = s.get('http://38.247.138.224:10017/api/method/frappe.desk.notifications.get_open_count', params={
        'doctype': 'Item',
        'name': item_code,
        'items': json.dumps(['Quotation', 'Sales Order', 'Sales Invoice', 'Delivery Note', 'Stock Entry'])
    })
    msg = r.json().get('message', {})
    links = msg.get('count', {}).get('external_links_found', [])
    timeline = msg.get('timeline_data', {})
    print(f"Item: {item_code:<25} | Status: {r.status_code} | Links: {len(links)} | Timeline Data Points: {len(timeline)}")
