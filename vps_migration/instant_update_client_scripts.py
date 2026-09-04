import requests
import json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

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

# Let's write a python runner via Server Script 'VM Test Globals'
escaped_script = full_script.replace('\\', '\\\\').replace("'''", "\\'\\'\\'")

server_runner = f"""
script_content = '''{escaped_script}'''

cs_list = frappe.get_all('Client Script', filters={{'name': ['like', '%Relationship Map%']}}, fields=['name'])
updated = []
for cs in cs_list:
    frappe.db.set_value('Client Script', cs.name, {{
        'script': script_content,
        'enabled': 1
    }}, update_modified=True)
    updated.append(cs.name)

frappe.db.commit()

frappe.response['message'] = {{
    'status': 'success',
    'updated': updated
}}
"""

res = s.put(f'{URL}/api/resource/Server%20Script/VM%20Test%20Globals', json={
    'script': server_runner,
    'disabled': 0
}, timeout=30)
print(f"Updated runner script: {res.status_code}")

run_res = s.get(f'{URL}/api/method/vm_test_globals', timeout=30)
print("Instant update result:", run_res.json())

cc_res = s.post(f'{URL}/api/method/frappe.handler.clear_cache', timeout=30)
print("Cleared cache:", cc_res.status_code)
