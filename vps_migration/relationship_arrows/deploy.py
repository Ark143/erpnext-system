"""Patch only the connector renderer, preserving each live VMS/P2P version."""
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
import requests

ROOT=Path(__file__).resolve().parents[2]
DRAW=(Path(__file__).parent/'draw_edges.js').read_text(encoding='utf-8')
START='      // Draw SVG Bezier Connecting Lines'
END='      // Bind node interactions'
def patch(script):
    if DRAW in script:return script
    if script.count(START)!=1 or script.count(END)!=1:
        raise ValueError('Unexpected renderer; refusing to overwrite')
    a=script.index(START);b=script.index(END,a)
    return script[:a]+DRAW+'\n\n'+script[b:]

if __name__=='__main__':
    canonical=ROOT/'frappe-bench/apps/vehicle_management/vehicle_management/public/js/vehicle_relationship_map.js'
    canonical.write_text(patch(canonical.read_text(encoding='utf-8')),encoding='utf-8')
    base=os.environ.get('ERPNEXT_URL','http://38.247.138.224:10017')
    session=requests.Session()
    session.post(base+'/api/method/login',data={'usr':os.environ.get('ERPNEXT_USER','Administrator'),'pwd':os.environ['ERPNEXT_PASSWORD']},timeout=30).raise_for_status()
    r=session.get(base+'/api/resource/Client Script',params={'fields':json.dumps(['name','enabled']),'limit_page_length':500},timeout=30);r.raise_for_status()
    names=[d['name'] for d in r.json()['data'] if d['enabled'] and d['name'].startswith(('SAP Relationship Map -','VM SAP Relationship Map Client'))]
    backup=ROOT/('backups/relationship_arrows_deploy_'+datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True)
    candidates=[]
    for name in names:
        url=base+'/api/resource/Client Script/'+quote(name,safe='')
        r=session.get(url,timeout=30);r.raise_for_status();doc=r.json()['data']
        fixed=patch(doc['script'])
        (backup/(name+'.json')).write_text(json.dumps(doc,indent=2),encoding='utf-8')
        candidates.append((url,doc,fixed))
    verified=[]
    for url,doc,fixed in candidates:
        r=session.get(url,timeout=30);r.raise_for_status()
        assert r.json()['data']['script']==doc['script'], 'Concurrent script change: '+doc['name']
        if fixed!=doc['script']:
            session.put(url,json={'script':fixed},timeout=30).raise_for_status()
        r=session.get(url,timeout=30);r.raise_for_status()
        assert r.json()['data']['script']==fixed
        verified.append({'name':doc['name'],'sha256':hashlib.sha256(fixed.encode()).hexdigest()})
        print('Verified:',doc['name'],flush=True)
    (backup/'verified.json').write_text(json.dumps(verified,indent=2))
    print('Backup:',backup)
