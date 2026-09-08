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

# Let's check Custom Scripts / Client Scripts with full fields
all_cs = get('resource/Client%20Script?limit_page_length=500&fields=["name","dt","script"]')
print("=== Client Scripts ===")
for cs in all_cs.get('data', []):
    print(f"DocType: {cs.get('dt')} | Name: {cs.get('name')}")
    print(cs.get('script'))
    print("--------------------------------------------------")

# Let's check Server Scripts with full fields
all_ss = get('resource/Server%20Script?limit_page_length=500&fields=["name","script_type","reference_doctype","script"]')
print("\n=== Server Scripts ===")
for ss in all_ss.get('data', []):
    print(f"Name: {ss.get('name')} | Type: {ss.get('script_type')} | Ref: {ss.get('reference_doctype')}")
    print(ss.get('script'))
    print("--------------------------------------------------")

# Let's check Custom Fields on standard DocTypes (Company, Customer, Supplier, Sales Invoice, Purchase Invoice, Item, etc.)
cfs = get('resource/Custom%20Field?limit_page_length=500&fields=["name","dt","fieldname","label","fieldtype","options"]')
print(f"\n=== All Custom Fields ({len(cfs.get('data', []))}) ===")
for cf in cfs.get('data', []):
    print(f"DocType: {cf.get('dt')} | Field: {cf.get('fieldname')} ({cf.get('label')}) | Type: {cf.get('fieldtype')}")
