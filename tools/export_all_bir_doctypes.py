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

bir_doctypes = [
    'BIR Cash Disbursement Journal',
    'BIR CDJ Invoice Row',
    'BIR CDJ Summary Row',
    'BIR Cash Receipt Journal',
    'BIR CRJ Invoice Row',
    'BIR CRJ Summary Row',
    'BIR Form 2307',
    'BIR Form 2307 Row',
    'BIR General Journal',
    'BIR GJ Entry Row',
    'BIR General Ledger',
    'BIR GL Entry Row',
    'BIR Purchases Book',
    'BIR Purchases Book Row',
    'BIR Sales Journal',
    'BIR Sales Journal Row',
    'BIR Sales Summary Row',
    'BIR VAT Summary',
    'BIR VAT Summary Row',
    'BIR VAT Summary Total Row',
    'BIR Withholding Summary',
    'BIR Withholding Summary Row'
]

os.makedirs('tools/bir_export/doctypes', exist_ok=True)
os.makedirs('tools/bir_export/records', exist_ok=True)

all_schemas = {}
for dt in bir_doctypes:
    res = get(f"resource/DocType/{urllib.parse.quote(dt)}")
    if 'data' in res:
        schema = res['data']
        all_schemas[dt] = schema
        with open(f"tools/bir_export/doctypes/{dt.replace(' ', '_')}.json", 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2)
        print(f"Exported DocType: {dt} ({len(schema.get('fields', []))} fields)")
    else:
        print(f"Failed to export DocType: {dt}: {res}")

    # Also export all records
    records = get(f"resource/{urllib.parse.quote(dt)}?limit_page_length=500")
    if 'data' in records:
        dt_records = []
        for r in records['data']:
            rec_detail = get(f"resource/{urllib.parse.quote(dt)}/{urllib.parse.quote(r['name'])}")
            if 'data' in rec_detail:
                dt_records.append(rec_detail['data'])
        with open(f"tools/bir_export/records/{dt.replace(' ', '_')}.json", 'w', encoding='utf-8') as f:
            json.dump(dt_records, f, indent=2)
        print(f"Exported {len(dt_records)} records for {dt}")

# Also export Invoicing Workspace
ws_res = get("resource/Workspace/Invoicing")
if 'data' in ws_res:
    with open("tools/bir_export/Invoicing_Workspace.json", 'w', encoding='utf-8') as f:
        json.dump(ws_res['data'], f, indent=2)
    print("Exported Invoicing Workspace")
