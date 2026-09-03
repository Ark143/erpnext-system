"""Confirm missing secret_key on VPS, then add a stable one (CSRF root-cause fix).

Server Scripts run under safe_exec: `frappe` is already available as a global
and `import` is disallowed. Use frappe.get_attr to reach update_site_config.
"""
import requests, json, time

BASE = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{BASE}/api/method/login', data={'usr': 'administrator', 'pwd': 'admin'}, timeout=30)

SCRIPT = '''def vm_fix_secret_key():
    out = {}
    try:
        sk = frappe.get_site_config().get("secret_key")
    except Exception as e:
        sk = None
        out["read_err"] = repr(e)
    out["was_set"] = bool(sk)
    out["len_before"] = len(sk) if sk else 0
    if not sk:
        try:
            newkey = frappe.generate_hash(length=32)
            update = frappe.get_attr("frappe.installer.update_site_config")
            update("secret_key", newkey)
            out["wrote"] = True
            out["newkey_len"] = len(newkey)
        except Exception as e:
            out["write_err"] = repr(e)
    try:
        out["len_after"] = len(frappe.get_site_config().get("secret_key") or "")
    except Exception as e:
        out["after_err"] = repr(e)
    frappe.response["message"] = out

vm_fix_secret_key()
'''

url = f'{BASE}/api/resource/Server%20Script/VM%20Fix%20Secret%20Key'
payload = {'doctype': 'Server Script', 'name': 'VM Fix Secret Key', 'script_type': 'API',
           'api_method': 'vm_fix_secret_key', 'allow_guest': 0, 'script': SCRIPT}
try:
    s.delete(url, timeout=60)
except Exception:
    pass
r = s.post(f'{BASE}/api/resource/Server%20Script', json=payload, timeout=60)
print('create HTTP', r.status_code)

result = None
for attempt in range(6):
    r2 = s.get(f'{BASE}/api/method/vm_fix_secret_key', timeout=60)
    d = r2.json()
    if 'message' in d:
        result = d['message']
        break
    print(f'  attempt {attempt}:', r2.text[:200])
    time.sleep(2)

print('RESULT:', json.dumps(result, indent=2))

try:
    s.delete(url, timeout=60)
    print('cleaned up temp script')
except Exception as e:
    print('cleanup note:', e)
