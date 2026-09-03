"""Fix POS Profile warehouse: 'Goods In Transit - X' -> 'Stores - X' per company.

The setup script's fallback (first non-group warehouse) landed on the Transit
warehouse, which is wrong for POS (sales deduct stock from the profile's warehouse).
Every company already has a proper 'Stores - X' warehouse. Backup-first, then fix,
then clean up the temp Server Script.
"""
import urllib.request, urllib.parse, json, time

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# ---- backup current POS profiles (backup-first rule) ----
r = opener.open('http://38.247.138.224:10017/api/resource/POS%20Profile?limit_page_length=100')
profs = json.loads(r.read().decode())['data']
backup = {}
for p in profs:
    pname = urllib.parse.quote(p['name'])
    doc = json.loads(opener.open('http://38.247.138.224:10017/api/resource/POS%20Profile/' + pname).read().decode())['data']
    backup[p['name']] = doc
backup_file = r'c:\Users\josem\erpnext-system\vps_migration\backups\pos_profiles_backup_' + str(int(time.time())) + '.json'
with open(backup_file, 'w', encoding='utf-8') as f:
    json.dump(backup, f, indent=2)
print('Backed up', len(backup), 'POS profiles ->', backup_file)

fix_script = """
def vm_fix_pos_profile_warehouses():
    results = []
    companies = frappe.get_all('Company', filters={'is_group': 0}, fields=['name'], order_by='name asc')
    for c in companies:
        cname = c['name']
        stores = frappe.get_all('Warehouse',
            filters={'company': cname, 'is_group': 0, 'name': ['like', 'Stores - %']},
            fields=['name'], limit=1)
        if not stores:
            results.append({'company': cname, 'status': 'no Stores warehouse'})
            continue
        stores_wh = stores[0]['name']
        profile_name = f'Vehicle POS - {cname}'
        if not frappe.db.exists('POS Profile', profile_name):
            results.append({'company': cname, 'status': 'no profile'})
            continue
        prof = frappe.get_doc('POS Profile', profile_name)
        old_wh = prof.warehouse
        if old_wh == stores_wh:
            results.append({'company': cname, 'profile': profile_name, 'old_warehouse': old_wh, 'new_warehouse': stores_wh, 'status': 'already correct'})
            continue
        prof.warehouse = stores_wh
        prof.save(ignore_permissions=True)
        results.append({'company': cname, 'profile': profile_name, 'old_warehouse': old_wh, 'new_warehouse': stores_wh, 'status': 'fixed'})
    frappe.db.commit()
    frappe.response['message'] = {'success': True, 'count': len(results), 'results': results}

vm_fix_pos_profile_warehouses()
"""

url = 'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Fix%20POS%20Profile%20Warehouses'
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
payload = json.dumps({
    'doctype': 'Server Script',
    'name': 'VM Fix POS Profile Warehouses',
    'script_type': 'API',
    'api_method': 'vm_fix_pos_profile_warehouses',
    'allow_guest': 0,
    'script': fix_script
}).encode()

try:
    req = urllib.request.Request(url, data=payload, headers=H, method='PUT')
    res = opener.open(req)
except urllib.error.HTTPError as e:
    if e.code == 404:
        req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Server%20Script', data=payload, headers=H, method='POST')
        res = opener.open(req)
    else:
        raise

print('Server script deployed, running fix...')

r_exec = opener.open('http://38.247.138.224:10017/api/method/vm_fix_pos_profile_warehouses')
output = json.loads(r_exec.read().decode())['message']
print('Fix executed:', output.get('count'), 'companies processed:')
for r in output['results']:
    print('  ' + r['status'].upper() + ' ' + r['company'] + ': ' + str(r.get('old_warehouse')) + ' -> ' + str(r.get('new_warehouse')))

# cleanup temp script
try:
    req_del = urllib.request.Request(url, headers=H, method='DELETE')
    opener.open(req_del)
    print('Cleaned up temp server script.')
except Exception as e:
    print('Note on cleanup:', e)
