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

# Let's delete obsolete individual Client Scripts and keep/update the main ones
target_names = [
  "SAP Relationship Map - Sales Invoice",
  "SAP Relationship Map - Vehicle Job Order",
  "SAP Relationship Map - Vehicle Estimate",
  "SAP Relationship Map - Vehicle Inspection",
  "SAP Relationship Map - Customer Vehicle",
  "SAP Relationship Map - Vehicle POS Invoice",
  "SAP Relationship Map - Payment Entry",
  "SAP Relationship Map - POS Invoice",
  "SAP Relationship Map - Stock Entry",
  "SAP Relationship Map - Quotation",
  "VM SAP Relationship Map Client"
]

for name in target_names:
    try:
        r = s.put(f"{URL}/api/resource/Client%20Script/{requests.utils.quote(name)}", json={
            "script": full_script,
            "enabled": 1
        }, timeout=30)
        print(f"[{r.status_code}] {name}")
    except Exception as e:
        print(f"Error {name}:", str(e))

# Clear website/app cache
try:
    s.post(f"{URL}/api/method/frappe.handler.clear_cache", timeout=30)
    print("[OK] Cache cleared on VPS.")
except Exception as e:
    print("Cache clear error:", str(e))
