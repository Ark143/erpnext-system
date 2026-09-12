import requests
import json
import urllib.parse

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

with open('frappe-bench/apps/vehicle_management/vehicle_management/www/appointment.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

payload = {
    'doctype': 'Web Page',
    'name': 'appointment',
    'title': 'ULTRA MRF — Appointment Scheduling & Customer VMS Portal',
    'route': 'appointment',
    'published': 1,
    'content_type': 'HTML',
    'main_section_html': html_content,
    'full_width': 1,
    'show_title': 0,
    'show_sidebar': 0
}

# Check if exists
r = s.get(f'{URL}/api/resource/Web%20Page/appointment')
if r.status_code == 200:
    res = s.put(f'{URL}/api/resource/Web%20Page/appointment', json=payload, timeout=60)
    print("Updated /appointment Web Page:", res.status_code)
else:
    res = s.post(f'{URL}/api/resource/Web%20Page', json=payload, timeout=60)
    print("Created /appointment Web Page:", res.status_code)

# Check route accessibility
r_test = s.get(f'{URL}/appointment', timeout=30)
print("HTTP GET /appointment Status:", r_test.status_code, "Length:", len(r_test.text))
