import requests
import json
import urllib.parse

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

with open('frappe-bench/apps/vehicle_management/vehicle_management/www/appointment.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

web_pages = [
    {
        'doctype': 'Web Page',
        'title': 'ULTRA MRF — Appointment Scheduling & Customer VMS Portal',
        'route': 'appointment',
        'published': 1,
        'content_type': 'HTML',
        'main_section_html': html_content
    },
    {
        'doctype': 'Web Page',
        'title': 'ULTRA MRF — Customer Service Booking',
        'route': 'booking',
        'published': 1,
        'content_type': 'HTML',
        'main_section_html': html_content
    },
    {
        'doctype': 'Web Page',
        'title': 'ULTRA MRF — Customer VMS Portal Hub',
        'route': 'customer-portal',
        'published': 1,
        'content_type': 'HTML',
        'main_section_html': html_content
    }
]

for wp in web_pages:
    route = wp['route']
    chk = s.get(f'{URL}/api/resource/Web%20Page/{route}')
    if chk.status_code == 200:
        s.put(f'{URL}/api/resource/Web%20Page/{route}', json=wp)
        print(f"[OK] Updated Web Page: /{route}")
    else:
        res = s.post(f'{URL}/api/resource/Web%20Page', json=wp)
        print(f"[OK] Created Web Page: /{route} (Status: {res.status_code})")

print("\nWeb Pages deployed successfully!")
