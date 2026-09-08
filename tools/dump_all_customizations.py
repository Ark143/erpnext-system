import urllib.request
import urllib.parse
import json
import os

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
data = urllib.parse.urlencode({
    'usr': 'josemangiliman.xansux.kun@gmail.com',
    'pwd': '8958698698'
}).encode('utf-8')
login_res = opener.open('https://demoerpnext.s.frappe.cloud/api/method/login', data=data)

def get(path):
    url = f'https://demoerpnext.s.frappe.cloud/api/{path}'
    try:
        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        res = opener.open(req)
        return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        return {'error': str(e)}

os.makedirs('tools/bir_export/client_scripts', exist_ok=True)
os.makedirs('tools/bir_export/server_scripts', exist_ok=True)
os.makedirs('tools/bir_export/custom_fields', exist_ok=True)
os.makedirs('tools/bir_export/property_setters', exist_ok=True)
os.makedirs('tools/bir_export/workspaces', exist_ok=True)

# 1. Client Scripts
all_cs = get('resource/Client%20Script?limit_page_length=500')
for cs in all_cs.get('data', []):
    cs_name = cs['name']
    cs_doc = get(f"resource/Client%20Script/{urllib.parse.quote(cs_name)}")
    if 'data' in cs_doc:
        with open(f"tools/bir_export/client_scripts/{cs_name.replace(' ', '_').replace('/', '_')}.json", 'w', encoding='utf-8') as f:
            json.dump(cs_doc['data'], f, indent=2)
        print(f"Saved Client Script: {cs_name} (DocType: {cs_doc['data'].get('dt')})")

# 2. Server Scripts
all_ss = get('resource/Server%20Script?limit_page_length=500')
for ss in all_ss.get('data', []):
    ss_name = ss['name']
    ss_doc = get(f"resource/Server%20Script/{urllib.parse.quote(ss_name)}")
    if 'data' in ss_doc:
        with open(f"tools/bir_export/server_scripts/{ss_name.replace(' ', '_').replace('/', '_')}.json", 'w', encoding='utf-8') as f:
            json.dump(ss_doc['data'], f, indent=2)
        print(f"Saved Server Script: {ss_name} (Type: {ss_doc['data'].get('script_type')})")

# 3. Custom Fields
all_cf = get('resource/Custom%20Field?limit_page_length=500')
for cf in all_cf.get('data', []):
    cf_name = cf['name']
    cf_doc = get(f"resource/Custom%20Field/{urllib.parse.quote(cf_name)}")
    if 'data' in cf_doc:
        with open(f"tools/bir_export/custom_fields/{cf_name.replace(' ', '_').replace('/', '_')}.json", 'w', encoding='utf-8') as f:
            json.dump(cf_doc['data'], f, indent=2)

print(f"Saved {len(all_cf.get('data', []))} Custom Fields")

# 4. Property Setters
all_ps = get('resource/Property%20Setter?limit_page_length=500')
for ps in all_ps.get('data', []):
    ps_name = ps['name']
    ps_doc = get(f"resource/Property%20Setter/{urllib.parse.quote(ps_name)}")
    if 'data' in ps_doc:
        with open(f"tools/bir_export/property_setters/{ps_name.replace(' ', '_').replace('/', '_')}.json", 'w', encoding='utf-8') as f:
            json.dump(ps_doc['data'], f, indent=2)

print(f"Saved {len(all_ps.get('data', []))} Property Setters")

# 5. Workspaces: Invoicing & Accounting
for ws_name in ['Invoicing', 'Financial Reports', 'Assets', 'Tax & Benefits']:
    ws_doc = get(f"resource/Workspace/{urllib.parse.quote(ws_name)}")
    if 'data' in ws_doc:
        with open(f"tools/bir_export/workspaces/{ws_name.replace(' ', '_')}.json", 'w', encoding='utf-8') as f:
            json.dump(ws_doc['data'], f, indent=2)
        print(f"Saved Workspace: {ws_name}")
