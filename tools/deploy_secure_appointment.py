"""Deploy the reviewed appointment module, compatibility paths and four page aliases.

Requires VPS_SSH_PASSWORD. Creates private backups and persistent Compose file mounts.
"""
from pathlib import Path
import json
import os
import shlex
import paramiko
import yaml

ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'frappe-bench/apps/vehicle_management/vehicle_management'
BASE='/home/administrator/erpdeploy'
DEST='/workspace/frappe-bench/apps/vehicle_management/vehicle_management'
ssh=paramiko.SSHClient();ssh.load_system_host_keys()
ssh.connect('38.247.138.224',port=10016,username='administrator',
    password=os.environ['VPS_SSH_PASSWORD'],look_for_keys=False,allow_agent=False,timeout=20)

def run(command,stdin=None):
    inp,out,err=ssh.exec_command(command,timeout=240)
    if stdin is not None:
        inp.write(stdin);inp.flush();inp.channel.shutdown_write()
    output=out.read().decode();error=err.read().decode();status=out.channel.recv_exit_status()
    if status: raise RuntimeError(error or output)
    return output

def remote_python(source):
    return run('docker exec -i -w /workspace/frappe-bench/sites erpdeploy-erpnext-1 python -',source)

run('mkdir -p '+BASE+'/portal_patch '+BASE+'/backups/portal_20260913')
sftp=ssh.open_sftp()
compose_path=BASE+'/docker-compose.yml'
with sftp.open(compose_path) as f: compose_bytes=f.read()
backup=BASE+'/backups/portal_20260913/docker-compose.before.yml'
try: sftp.stat(backup)
except FileNotFoundError:
    with sftp.open(backup,'wb') as f: f.write(compose_bytes)
compose=yaml.safe_load(compose_bytes)
volumes=compose['services']['erpnext'].setdefault('volumes',[])
mounted={m['Destination'] for m in json.loads(run('docker inspect erpdeploy-erpnext-1'))[0]['Mounts']}
files=['secure_portal.py','api/__init__.py','api/portal.py','www/appointment.html',
    'vehicle_management/doctype/vehicle_appointment/vehicle_appointment.py']
for relative in files:
    target=DEST+'/'+relative
    host=BASE+'/portal_patch/'+relative.replace('/','__')
    sftp.put(str(APP/relative),host)
    run('docker exec erpdeploy-erpnext-1 mkdir -p '+shlex.quote(target.rsplit('/',1)[0]))
    if target not in mounted:
        run('docker cp '+shlex.quote(host)+' erpdeploy-erpnext-1:'+shlex.quote(target))
    volumes[:]=[v for v in volumes if not (isinstance(v,str) and ':'+target+':' in v)]
    volumes.append(host+':'+target+':ro')

# Preserve the installed Frappe version and patch only the contact scheduling flag.
user_path='/workspace/frappe-bench/apps/frappe/frappe/core/doctype/user/user.py'
user_source=run('docker exec erpdeploy-erpnext-1 cat '+user_path)
old='now = frappe.in_test or frappe.flags.in_install'
new=old+' or self.flags.create_contact_now'
assert old in user_source
if new not in user_source: user_source=user_source.replace(old,new,1)
user_host=BASE+'/portal_patch/user.py'
with sftp.open(user_host,'w') as f:f.write(user_source)
if user_path not in mounted: run('docker cp '+user_host+' erpdeploy-erpnext-1:'+user_path)
volumes[:]=[v for v in volumes if not (isinstance(v,str) and ':'+user_path+':' in v)]
volumes.append(user_host+':'+user_path+':ro')

html=(APP/'www/appointment.html').read_text(encoding='utf-8')
theme=(APP/'public/css/appointment_theme.css').read_text(encoding='utf-8')
source='''import frappe
from pathlib import Path
frappe.init(site='site1.local',sites_path='/workspace/frappe-bench/sites');frappe.connect();frappe.set_user('Administrator')
root=Path('/workspace/frappe-bench/sites/site1.local/private/backups/secure_portal_20260913');root.mkdir(parents=True,exist_ok=True)
for name in ['vehicle-management-system','vm-dashboard','vm-company-dashboard','vehicle-management-system-portal']:
    doc=frappe.get_doc('Web Page',name)
    file=root/(name+'.json')
    if not file.exists():file.write_text(doc.as_json())
    frappe.db.set_value('Web Page',name,{'main_section':HTML_VALUE,'main_section_html':HTML_VALUE,'css':CSS_VALUE,'javascript':''})
for row in frappe.get_all('Server Script',filters={'api_method':['like','vehicle_management.api.portal.%']},fields=['name']):
    doc=frappe.get_doc('Server Script',row.name)
    file=root/('script-'+row.name+'.json')
    if not file.exists():file.write_text(doc.as_json())
    if not doc.disabled:
        doc.disabled=1;doc.save(ignore_permissions=True)
# Preserve employee access; "All" also grants every new Website User access.
for dt in ['Vehicle Appointment','Sales Invoice','POS Invoice']:
    for table in ['DocPerm','Custom DocPerm']:
        for row in frappe.get_all(table,filters={'parent':dt,'role':'All'},fields=['name']):
            doc=frappe.get_doc(table,row.name)
            file=root/(table+'-'+row.name+'.json')
            if not file.exists():file.write_text(doc.as_json())
            frappe.db.set_value(table,row.name,'role','Desk User')
    frappe.clear_cache(doctype=dt)
frappe.db.commit();frappe.clear_cache()
from frappe.website.utils import clear_website_cache
clear_website_cache()
frappe.destroy()
print('Four portal routes updated; legacy guest scripts disabled; employee access preserved.')
'''.replace('HTML_VALUE',repr(html)).replace('CSS_VALUE',repr(theme))
print(remote_python(source))
with sftp.open(compose_path,'w') as f:f.write(yaml.safe_dump(compose,sort_keys=False))
sftp.close()
print(run('cd '+BASE+' && docker compose up -d --no-deps erpnext'))
ssh.close()
print('Portal deployed with persistent source mounts.')
