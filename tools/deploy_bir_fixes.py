"""Deploy the reviewed BIR fixes, with backup, conflict checks and readback.

Requires ERPNEXT_PASSWORD. No accounting transactions are created or updated.
"""
import json
import hashlib
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
import requests

ROOT = Path(__file__).resolve().parent.parent
FIXES = ROOT / 'tools/bir_fixes'
BASE = os.environ.get('ERPNEXT_URL', 'http://38.247.138.224:10017').rstrip('/')
session = requests.Session()
session.post(BASE+'/api/method/login', data={
    'usr': os.environ.get('ERPNEXT_USER', 'Administrator'),
    'pwd': os.environ['ERPNEXT_PASSWORD']}, timeout=30).raise_for_status()

def resource(dt, name):
    return BASE+'/api/resource/'+quote(dt, safe='')+'/'+quote(name, safe='')

changes = []
baseline=json.loads((FIXES/'baseline_hashes.json').read_text())
backup = ROOT / ('backups/bir_fix_deploy_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True)
for dt, filename, field in [('Client Script','client_scripts.json','script'),('Print Format','print_formats.json','html')]:
    saved = []
    for candidate in json.loads((FIXES/filename).read_text()):
        url = resource(dt,candidate['name'])
        response=session.get(url, timeout=30);response.raise_for_status();live=response.json()['data']
        if live[field]!=candidate[field] and hashlib.sha256(live[field].encode()).hexdigest()!=baseline[dt][candidate['name']]:
            raise RuntimeError('Concurrent edit detected: '+candidate['name'])
        saved.append(live)
        changes.append((url,field,candidate[field],candidate['name']))
    (backup/(dt.replace(' ','_')+'.json')).write_text(json.dumps(saved,indent=2),encoding='utf-8')

# Restore the original local Form 2307 background through the supported upload API.
asset_url='/files/bir_2307_restored_20260909.png'
asset=(FIXES/'assets/bir_2307_page1.png').read_bytes()
existing=session.get(BASE+asset_url,timeout=30)
if existing.status_code!=200 or existing.content!=asset:
    response=session.post(BASE+'/api/method/upload_file',files={'file':('bir_2307_restored_20260909.png',asset,'image/png')},data={'is_private':0},timeout=60)
    response.raise_for_status()
    if response.json()['message']['file_url']!=asset_url:
        raise RuntimeError('Unexpected upload URL; inspect before deployment')
response=session.get(BASE+asset_url,timeout=30);response.raise_for_status()
assert response.content==asset, 'Uploaded background differs'
completed=[]
try:
    for url,field,value,name in changes:
        response=session.put(url,json={field:value},timeout=30);response.raise_for_status()
        response=session.get(url,timeout=30);response.raise_for_status()
        assert response.json()['data'][field]==value, 'Readback mismatch: '+name
        completed.append(name)
        print('Verified deployed:',name)
finally:
    (backup/'deployment.json').write_text(json.dumps({'completed':completed,'asset_url':asset_url},indent=2))
    print('Rollback backup:',backup)
