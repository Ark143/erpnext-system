import requests
import json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=45)

with open('c:/Users/josem/erpnext-system/frappe-bench/apps/vehicle_management/vehicle_management/public/js/vehicle_relationship_map.js', 'r', encoding='utf-8') as f:
    js_code = f.read()

with open('c:/Users/josem/erpnext-system/frappe-bench/apps/vehicle_management/vehicle_management/public/css/vehicle_management_desk.css', 'r', encoding='utf-8') as f:
    css_code = f.read()

css_clean = css_code.replace('`', '\\`')

full_script = f"""
frappe.provide('frappe.ui.form');

if (!$('#sap-rel-map-styles').length) {{
  $('head').append(`<style id="sap-rel-map-styles">{css_clean}</style>`);
}}

{js_code}
"""

# Fetch all Client Scripts
cs_list = s.get(f'{URL}/api/resource/Client%20Script', params={'limit_page_length': 100, 'fields': json.dumps(['name', 'dt', 'enabled'])}).json().get('data', [])

for cs in cs_list:
    name = cs.get('name')
    if 'Relationship Map' in name or 'SAP' in name or 'VMS' in name:
        res = s.put(f'{URL}/api/resource/Client%20Script/{requests.utils.quote(name)}', json={
            'script': full_script,
            'enabled': 1
        }, timeout=30)
        print(f"Updated Client Script '{name}': {res.status_code}")

# Clear cache
clear_res = s.post(f'{URL}/api/method/frappe.handler.clear_cache', timeout=30)
print("Cleared cache:", clear_res.status_code)
