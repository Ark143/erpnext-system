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

# 1. Print Formats
pfs = get('resource/Print Format?limit_page_length=500')
print("=== All Print Formats ===")
for p in pfs.get('data', []):
    pf_doc = get(f"resource/Print Format/{urllib.parse.quote(p['name'])}")
    data_doc = pf_doc.get('data', {})
    print(f"PF: {p['name']} | DocType: {data_doc.get('doc_type')} | Standard: {data_doc.get('standard')} | Custom: {data_doc.get('custom_format')} | Type: {data_doc.get('print_format_type')}")

# 2. Check Invoicing Workspace cards & BIR links
invoicing_ws = get('resource/Workspace/Invoicing')
print("\n=== Invoicing Workspace Links ===")
for link in invoicing_ws.get('data', {}).get('links', []):
    print(f"Type: {link.get('type')} | Label: {link.get('label')} | Link To: {link.get('link_to')}")

# 3. Check Accounting Workspace
acct_ws = get('resource/Workspace/Accounting')
print("\n=== Accounting Workspace Links ===")
for link in acct_ws.get('data', {}).get('links', []):
    print(f"Type: {link.get('type')} | Label: {link.get('label')} | Link To: {link.get('link_to')}")

# 4. Check all workspaces on demo to see if there is a 'BIR' or 'Tax' workspace
all_ws = get('resource/Workspace?limit_page_length=200')
print("\n=== All Workspaces ===")
for w in all_ws.get('data', []):
    print(w['name'])

# 5. Check if there are any documents created in these BIR DocTypes on demoerpnext
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

print("\n=== BIR Records Count & Sample Data ===")
for dt in bir_doctypes:
    records = get(f"resource/{urllib.parse.quote(dt)}?limit_page_length=5")
    data_list = records.get('data', [])
    print(f"DocType: {dt} | Count: {len(data_list)}")
    if data_list:
        print(f"  Sample record: {data_list[0]['name']}")
