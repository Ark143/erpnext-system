import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
res = op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)
print("[OK] Logged into VPS.")

# DocType Event for Customer Vehicle: before_validate
doc_event_script = """
if doc.get('make') and not frappe.db.exists('Vehicle Make', doc.get('make')):
    try:
        mk_doc = frappe.get_doc({
            'doctype': 'Vehicle Make',
            'make_name': doc.get('make'),
            'name': doc.get('make')
        })
        mk_doc.insert(ignore_permissions=True)
    except Exception:
        pass

if doc.get('model') and not frappe.db.exists('Vehicle Model', doc.get('model')):
    try:
        mdl = doc.get('model')
        mk = doc.get('make') or 'Other'
        m_name = mdl
        if '-' in mdl:
            parts = mdl.split('-', 1)
            if not doc.get('make'):
                mk = parts[0].strip()
            m_name = parts[1].strip()

        m_doc = frappe.get_doc({
            'doctype': 'Vehicle Model',
            'make': mk,
            'model_name': m_name
        })
        m_doc.insert(ignore_permissions=True)
        doc.model = m_doc.name
    except Exception:
        pass
"""

script_payload = {
    "name": "VM Auto Resolve Vehicle Models",
    "script_type": "DocType Event",
    "reference_doctype": "Customer Vehicle",
    "doctype_event": "Before Validate",
    "disabled": 0,
    "script": doc_event_script
}

try:
    up_req = urllib.request.Request(f'{URL}/api/resource/Server%20Script/VM%20Auto%20Resolve%20Vehicle%20Models', data=json.dumps(script_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='PUT')
    op.open(up_req, timeout=15)
    print("[OK] Server Script 'VM Auto Resolve Vehicle Models' updated.")
except Exception:
    create_req = urllib.request.Request(f'{URL}/api/resource/Server%20Script', data=json.dumps(script_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='POST')
    op.open(create_req, timeout=15)
    print("[OK] Server Script 'VM Auto Resolve Vehicle Models' created.")
