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
print("Login status:", login_res.getcode())

def get(path):
    url = f'https://demoerpnext.s.frappe.cloud/api/{path}'
    try:
        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        res = opener.open(req)
        return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        return {'error': str(e)}

def get_doc(doctype, name):
    path = f"resource/{urllib.parse.quote(doctype)}/{urllib.parse.quote(name)}"
    return get(path)

# 1. Check all modules
mods = get('resource/Module Def?limit_page_length=500')
print("\n=== Modules ===")
for m in mods.get('data', []):
    name = m.get('name', '')
    if any(k in name.lower() for k in ['bir', 'tax', 'ph', 'custom', 'invoice', 'invoicing', 'filipino', 'regional']):
        print("Matching Module:", name)

# 2. Check all custom doctypes
custom_dts = get('resource/DocType?filters=[["custom","=",1]]&fields=["name","module","custom"]&limit_page_length=200')
print("\n=== Custom DocTypes ===")
for dt in custom_dts.get('data', []):
    print("Custom DocType:", dt)

# 3. Check all DocTypes matching BIR / Tax / Regional
all_dts = get('resource/DocType?limit_page_length=2000')
print(f"\n=== Total DocTypes on demo: {len(all_dts.get('data', []))} ===")
for dt in all_dts.get('data', []):
    name = dt.get('name', '')
    if any(k in name.lower() for k in ['bir', '2307', '2306', '2550', 'cas', 'withholding', 'philippine', 'tax withholding']):
        print("BIR DocType:", name)

# 4. Check Workspaces
ws_res = get('resource/Workspace?fields=["name","title","module","category","is_standard"]&limit_page_length=200')
print("\n=== Workspaces ===")
for w in ws_res.get('data', []):
    title = (w.get('title') or '').lower()
    name = w.get('name', '').lower()
    if any(k in name or k in title for k in ['bir', 'invoicing', 'invoice', 'tax', 'accounting']):
        print("Workspace:", w)

# 5. Check Print Formats
pf_res = get('resource/Print Format?fields=["name","doc_type","module","standard","custom_format"]&limit_page_length=500')
print("\n=== Print Formats ===")
for pf in pf_res.get('data', []):
    name = pf.get('name', '')
    dt = pf.get('doc_type', '')
    if any(k in name.lower() or k in dt.lower() for k in ['bir', '2307', '2306', 'invoice', 'receipt', 'withholding', 'vat']):
        print("Print Format:", pf)

# 6. Check Reports
rep_res = get('resource/Report?fields=["name","ref_doctype","module","is_standard","report_type"]&limit_page_length=500')
print("\n=== Reports ===")
for r in rep_res.get('data', []):
    name = r.get('name', '')
    ref = (r.get('ref_doctype') or '').lower()
    if any(k in name.lower() or k in ref for k in ['bir', '2307', '2306', 'cas', 'vat', 'sales book', 'purchase book', 'withholding', 'relief', 'slsp']):
        print("Report:", r)

# 7. Check Client Scripts
cs_res = get('resource/Client Script?fields=["name","dt","enabled","module"]&limit_page_length=200')
print("\n=== Client Scripts ===")
for cs in cs_res.get('data', []):
    print("Client Script:", cs)

# 8. Check Server Scripts
ss_res = get('resource/Server Script?fields=["name","script_type","reference_doctype","disabled","module"]&limit_page_length=200')
print("\n=== Server Scripts ===")
for ss in ss_res.get('data', []):
    print("Server Script:", ss)

# 9. Check Custom Fields
cf_res = get('resource/Custom Field?fields=["name","dt","fieldname","label","fieldtype","module"]&limit_page_length=1000')
print(f"\n=== Custom Fields ({len(cf_res.get('data', []))}) ===")
for cf in cf_res.get('data', []):
    fname = cf.get('fieldname', '')
    flabel = (cf.get('label') or '').lower()
    dt = cf.get('dt', '')
    if any(k in fname.lower() or k in flabel or k in dt.lower() for k in ['bir', 'tin', '2307', '2306', 'atc', 'withholding', 'vat', 'cor', 'rdo', 'permit', 'serial', 'cas']):
        print("Custom Field:", cf)

# 10. Check Property Setters
ps_res = get('resource/Property Setter?fields=["name","doc_type","field_name","property","value","module"]&limit_page_length=500')
print(f"\n=== Property Setters ({len(ps_res.get('data', []))}) ===")
for ps in ps_res.get('data', []):
    dt = ps.get('doc_type', '')
    fn = ps.get('field_name', '')
    if any(k in dt.lower() or k in (fn or '').lower() for k in ['invoice', 'tax', 'sales', 'purchase', 'customer', 'supplier', 'item', 'bir']):
        print("Property Setter:", ps)
