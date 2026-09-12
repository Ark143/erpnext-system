import requests
import json
import urllib.parse

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

updater_script = """
docname = frappe.form_dict.get('docname')
title = frappe.form_dict.get('title')
route = frappe.form_dict.get('route')
html = frappe.form_dict.get('html')

if not route:
    frappe.response['message'] = {'error': 'Route required'}
else:
    # Update target document directly
    frappe.db.set_value("Web Page", docname, {
        "title": title or "ULTRA MRF Portal",
        "route": route,
        "published": 1,
        "content_type": "HTML",
        "main_section_html": html,
        "full_width": 1,
        "show_title": 0,
        "show_sidebar": 0
    }, update_modified=False)
    frappe.db.commit()
    frappe.response['message'] = {'success': True, 'action': 'updated', 'name': docname, 'route': route}
"""

s.put(f'{URL}/api/resource/Server%20Script/vm_update_web_page', json={
    'doctype': 'Server Script',
    'name': 'vm_update_web_page',
    'script_type': 'API',
    'api_method': 'vm_update_web_page',
    'allow_guest': 0,
    'disabled': 0,
    'script': updater_script
})

with open('frappe-bench/apps/vehicle_management/vehicle_management/www/appointment.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Map existing Web Page records to our routes
pages = [
    ('vehicle-management-system', 'appointment', 'ULTRA MRF — Appointment Scheduling & Customer VMS Portal'),
    ('vm-dashboard', 'booking', 'ULTRA MRF — Service Booking Portal'),
    ('vm-company-dashboard', 'customer-portal', 'ULTRA MRF — Customer VMS Portal Hub'),
    ('vehicle-management-system-portal', 'vms-portal', 'ULTRA MRF — Vehicle Management System Portal')
]

for docname, route, title in pages:
    r_up = s.post(f'{URL}/api/method/vm_update_web_page', data={
        'docname': docname,
        'title': title,
        'route': route,
        'html': html_content
    })
    print(f"Deployed {docname} -> /{route}:", r_up.json().get('message') or r_up.json().get('exception'))

# Test fetching each route
for docname, route, title in pages:
    r_t = s.get(f'{URL}/{route}')
    print(f"Verified GET /{route} -> Status: {r_t.status_code}, Length: {len(r_t.text)}")
