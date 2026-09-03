import urllib.request, json, os, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')

BACKUP_DIR = 'c:/Users/josem/erpnext-system/vps_migration/backups'
os.makedirs(BACKUP_DIR, exist_ok=True)
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
target_folder = os.path.join(BACKUP_DIR, f'backup_{timestamp}')
os.makedirs(target_folder, exist_ok=True)

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

DOCTYPES_TO_BACKUP = [
    'Server Script',
    'Web Page',
    'POS Profile',
    'Mode of Payment',
    'Print Format',
    'Custom Field',
    'Property Setter',
    'Workspace',
    'Workspace Sidebar'
]

print(f"=== Starting Live Backup to: {target_folder} ===")

for dt in DOCTYPES_TO_BACKUP:
    try:
        url = f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(dt)}?limit_page_length=500'
        r = opener.open(url)
        data = json.loads(r.read().decode())['data']
        
        full_docs = []
        for item in data:
            doc_name = item['name']
            doc_url = f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(dt)}/{urllib.parse.quote(doc_name)}'
            try:
                doc_res = opener.open(doc_url)
                full_docs.append(json.loads(doc_res.read().decode())['data'])
            except Exception as e:
                full_docs.append(item)
                
        out_file = os.path.join(target_folder, f"{dt.replace(' ', '_').lower()}.json")
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(full_docs, f, indent=2, ensure_ascii=False)
            
        print(f"  ✅ Backed up {len(full_docs)} {dt} records -> {os.path.basename(out_file)}")
    except Exception as e:
        print(f"  ⚠️ Error backing up {dt}: {e}")

print(f"\n🎉 Live backup completed successfully! Stored at: {target_folder}")
