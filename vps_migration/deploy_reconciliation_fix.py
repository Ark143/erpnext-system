import json
import urllib.parse
import urllib.request
import http.cookiejar
from datetime import datetime
from pathlib import Path

BASE = 'http://38.247.138.224:10017'
ROOT = Path(__file__).resolve().parents[1]
WORK = Path(r'C:/Users/josem/Documents/Codex/2026-09-06/can-you-add-openai-to-my/work/reconciliation')
STAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
BACKUP = ROOT / 'vps_migration' / 'backups' / ('reconciliation_deploy_' + STAMP)
BACKUP.mkdir(parents=True, exist_ok=True)

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}

def call(path, method='GET', payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, headers=H, method=method)
    with opener.open(req, timeout=60) as res:
        raw = res.read().decode()
        return json.loads(raw) if raw else {}

login_headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
opener.open(urllib.request.Request(BASE + '/api/method/login', data=b'usr=Administrator&pwd=admin', headers=login_headers), timeout=60).read()

script_names = {
    'vm_pos_get_shift': 'vm_pos_get_shift_new.py',
    'vm_pos_close_shift': 'vm_pos_close_shift_new.py',
    'vm_pos_open_shift': 'vm_pos_open_shift_new.py',
    'vm_pos_create_invoice': 'vm_pos_create_invoice_new.py',
    'vm_pos_history': 'vm_pos_history_new.py',
}

listing = call('/api/resource/Server%20Script?fields=[%22name%22,%22api_method%22]&limit_page_length=200')
by_api = {row.get('api_method'): row.get('name') for row in listing.get('data', [])}
for api_method, filename in script_names.items():
    name = by_api.get(api_method)
    if not name:
        raise RuntimeError('Missing Server Script for ' + api_method)
    old = call('/api/resource/Server%20Script/' + urllib.parse.quote(name))
    (BACKUP / (api_method + '_backup.json')).write_text(json.dumps(old.get('data', {}), indent=2), encoding='utf-8')
    script = (WORK / filename).read_text(encoding='utf-8')
    call('/api/resource/Server%20Script/' + urllib.parse.quote(name), 'PUT', {'script': script, 'disabled': 0})

page = call('/api/resource/Web%20Page/vehicle-pos-terminal')
(BACKUP / 'vehicle-pos-terminal_backup.json').write_text(json.dumps(page.get('data', {}), indent=2), encoding='utf-8')
html = (WORK / 'pos_after.html').read_text(encoding='utf-8')
call('/api/resource/Web%20Page/vehicle-pos-terminal', 'PUT', {'main_section_html': html})

for temp_name in ['POS Reconciliation Preview Check 20260906', 'POS Reconciliation Close Check 20260906']:
    try:
        call('/api/resource/Server%20Script/' + urllib.parse.quote(temp_name), 'DELETE')
    except Exception:
        pass

verified = {}
for api_method in script_names:
    name = by_api[api_method]
    current = call('/api/resource/Server%20Script/' + urllib.parse.quote(name)).get('data', {})
    verified[api_method] = 'def recon_user(' in current.get('script', '') and 'def recon_candidates(' in current.get('script', '')
live_page = call('/api/resource/Web%20Page/vehicle-pos-terminal').get('data', {})
verified['web_page'] = 'vpos-recon-modal' in live_page.get('main_section_html', '')
(BACKUP / 'deployment_verification.json').write_text(json.dumps(verified, indent=2), encoding='utf-8')
print(json.dumps({'backup': str(BACKUP), 'verified': verified}, indent=2))
