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

# 1. Check ALL Client Scripts
cs_list = get('resource/Client Script?limit_page_length=500')
print("=== Client Scripts on Demo ===")
for cs in cs_list.get('data', []):
    cs_doc = get(f"resource/Client Script/{urllib.parse.quote(cs['name'])}")
    data = cs_doc.get('data', {})
    print(f"Name: {cs['name']} | DocType: {data.get('dt')} | Enabled: {data.get('enabled')}")
    # print code snippet
    code = data.get('script', '')
    print(f"Code preview ({len(code)} chars):\n{code[:300]}\n")

# 2. Check ALL Server Scripts
ss_list = get('resource/Server Script?limit_page_length=500')
print("\n=== Server Scripts on Demo ===")
for ss in ss_list.get('data', []):
    ss_doc = get(f"resource/Server Script/{urllib.parse.quote(ss['name'])}")
    data = ss_doc.get('data', {})
    print(f"Name: {ss['name']} | Type: {data.get('script_type')} | Ref DocType: {data.get('reference_doctype')} | Disabled: {data.get('disabled')}")
    code = data.get('script', '')
    print(f"Code preview ({len(code)} chars):\n{code[:300]}\n")

# 3. Check Web Pages / Custom Pages
pages = get('resource/Page?limit_page_length=500')
print("\n=== Custom Pages ===")
for p in pages.get('data', []):
    if any(k in p['name'].lower() for k in ['bir', 'invoice', 'invoicing', 'tax']):
        print(p)

# 4. Check Print Formats again
pfs = get('resource/Print Format?limit_page_length=500')
print("\n=== Print Formats ===")
for p in pfs.get('data', []):
    pf_doc = get(f"resource/Print Format/{urllib.parse.quote(p['name'])}")
    data = pf_doc.get('data', {})
    print(f"PF: {p['name']} | DocType: {data.get('doc_type')} | Standard: {data.get('standard')}")
    if data.get('html') or data.get('raw_printing'):
        print(f"HTML snippet: {str(data.get('html'))[:200]}")
