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

# Check all Print Designer Formats if any
pdf_res = get('resource/Print Designer Format?limit_page_length=200')
print("=== Print Designer Format ===")
print(pdf_res)

# Check custom Print Formats
pfs = get('resource/Print Format?filters=[["custom_format","=",1]]&limit_page_length=200')
print("\n=== Custom Print Formats ===")
print(pfs)

all_pfs = get('resource/Print Format?limit_page_length=200')
print(f"\n=== Total Print Formats: {len(all_pfs.get('data', []))} ===")
for p in all_pfs.get('data', []):
    print(p['name'])

# Check full sample data of BIR records to see what fields & tables look like
bir_samples = [
    'BIR Cash Disbursement Journal',
    'BIR Cash Receipt Journal',
    'BIR Form 2307',
    'BIR General Journal',
    'BIR General Ledger',
    'BIR Purchases Book',
    'BIR Sales Journal',
    'BIR VAT Summary',
    'BIR Withholding Summary'
]

print("\n=== Sample Records Content ===")
for dt in bir_samples:
    records = get(f"resource/{urllib.parse.quote(dt)}?limit_page_length=1")
    if records.get('data'):
        rec_name = records['data'][0]['name']
        rec_detail = get(f"resource/{urllib.parse.quote(dt)}/{urllib.parse.quote(rec_name)}")
        print(f"\n--- {dt} ({rec_name}) ---")
        print(json.dumps(rec_detail.get('data', {}), indent=2))
