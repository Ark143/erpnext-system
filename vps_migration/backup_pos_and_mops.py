import urllib.request, urllib.parse, json, time

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

backup = {}

# Backup all POS Profiles
r = opener.open('http://38.247.138.224:10017/api/resource/POS%20Profile?limit_page_length=100')
profs = json.loads(r.read().decode())['data']
backup['pos_profiles'] = {}
for p in profs:
    pname = urllib.parse.quote(p['name'])
    doc = json.loads(opener.open('http://38.247.138.224:10017/api/resource/POS%20Profile/' + pname).read().decode())['data']
    backup['pos_profiles'][p['name']] = doc

# Backup all Modes of Payment
r2 = opener.open('http://38.247.138.224:10017/api/resource/Mode%20of%20Payment?limit_page_length=100')
mops = json.loads(r2.read().decode())['data']
backup['modes_of_payment'] = {}
for m in mops:
    mname = urllib.parse.quote(m['name'])
    doc = json.loads(opener.open('http://38.247.138.224:10017/api/resource/Mode%20of%20Payment/' + mname).read().decode())['data']
    backup['modes_of_payment'][m['name']] = doc

backup_file = r'c:\Users\josem\erpnext-system\vps_migration\backups\pos_profiles_and_mop_backup_' + str(int(time.time())) + '.json'
with open(backup_file, 'w', encoding='utf-8') as f:
    json.dump(backup, f, indent=2)

print('Successfully backed up', len(backup['pos_profiles']), 'POS Profiles and', len(backup['modes_of_payment']), 'Modes of Payment to', backup_file)
