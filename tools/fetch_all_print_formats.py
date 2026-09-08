import glob
import json
import urllib.request
import urllib.parse
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

os.makedirs('tools/bir_export/print_formats', exist_ok=True)

files = glob.glob('tools/bir_export/doctypes/*.json')
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
        dpf = data.get('default_print_format')
        name = data.get('name')
        print(f"{name} -> default_print_format: {dpf}")
        if dpf:
            pf_doc = get(f"resource/Print%20Format/{urllib.parse.quote(dpf)}")
            if 'data' in pf_doc:
                with open(f"tools/bir_export/print_formats/{dpf.replace(' ', '_')}.json", 'w', encoding='utf-8') as pff:
                    json.dump(pf_doc['data'], pff, indent=2)
                print(f"   Saved Print Format: {dpf}")
            else:
                print(f"   Failed to fetch Print Format {dpf}: {pf_doc}")

# Also check for all Print Formats list properly encoded
pf_list = get('resource/Print%20Format?limit_page_length=500')
print(f"\n=== Total Print Formats on Demo: {len(pf_list.get('data', []))} ===")
for pf in pf_list.get('data', []):
    pf_name = pf.get('name', '')
    pf_doc = get(f"resource/Print%20Format/{urllib.parse.quote(pf_name)}")
    if 'data' in pf_doc:
        dt = pf_doc['data'].get('doc_type', '')
        print(f"Print Format: {pf_name} | DocType: {dt} | Type: {pf_doc['data'].get('print_format_type')}")
        with open(f"tools/bir_export/print_formats/{pf_name.replace(' ', '_')}.json", 'w', encoding='utf-8') as pff:
            json.dump(pf_doc['data'], pff, indent=2)
