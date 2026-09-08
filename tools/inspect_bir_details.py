import urllib.request
import urllib.parse
import json

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

# Check Print Formats in detail
all_pfs = get('resource/Print Format?limit_page_length=500&fields=["name","doc_type","module","standard","custom_format","print_format_type"]')
print("=== All Print Formats on Demo ===")
for pf in all_pfs.get('data', []):
    print(pf)

# Check all Workspaces in detail
all_ws = get('resource/Workspace?limit_page_length=200&fields=["name","title","module","category","is_standard","public"]')
print("\n=== All Workspaces on Demo ===")
for ws in all_ws.get('data', []):
    print(ws)

# Check Desk Page / Invoicing Workspace
invoicing_ws = get('resource/Workspace/Invoicing')
print("\n=== Invoicing Workspace Detail ===")
print(json.dumps(invoicing_ws, indent=2))

# Check Bank Loan DocTypes too if relevant
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

print("\n=== BIR DocTypes Schema Export ===")
for dt in bir_doctypes:
    schema = get(f'resource/DocType/{urllib.parse.quote(dt)}')
    fields_count = len(schema.get('data', {}).get('fields', []))
    print(f"DocType: {dt} | Fields: {fields_count} | Is Submittable: {schema.get('data', {}).get('is_submittable')} | Module: {schema.get('data', {}).get('module')}")
