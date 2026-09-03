import urllib.request, urllib.parse, json, time

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

scripts_to_backup = ['VM POS Items', 'VM POS Items API', 'VM POS Stock', 'VM POS History', 'VM POS Create Invoice']
backup = {}

for sname in scripts_to_backup:
    try:
        url = 'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote(sname)
        doc = json.loads(opener.open(url).read().decode())['data']
        backup[sname] = doc
    except Exception as e:
        print(f'Error backing up {sname}: {e}')

backup_file = r'c:\Users\josem\erpnext-system\vps_migration\backups\pos_stock_and_receipt_scripts_backup_' + str(int(time.time())) + '.json'
with open(backup_file, 'w', encoding='utf-8') as f:
    json.dump(backup, f, indent=2)

print('Successfully backed up server scripts to', backup_file)
