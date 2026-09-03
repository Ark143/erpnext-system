"""
Fix script:
1. Create Vehicle Management Workspace Sidebar with items (Customer Vehicle, Vehicle Job Order, Vehicle Inspection, etc.)
2. Fix Mode of Payment accounts for missing companies (BDO, Bank Transfer, GCash, Maya, Card, Credit Card)
"""
import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# ============================================================
# STEP 1: BACKUP existing data before making any changes
# ============================================================
backup = {}

# Backup Vehicle Management Desktop Icon
r = opener.open('http://38.247.138.224:10017/api/resource/Desktop%20Icon/Vehicle%20Management')
backup['desktop_icon_vehicle_management'] = json.loads(r.read().decode())['data']

# Backup Vehicle Management Workspace
r2 = opener.open('http://38.247.138.224:10017/api/resource/Workspace/Vehicle%20Management')
backup['workspace_vehicle_management'] = json.loads(r2.read().decode())['data']

# Backup MoP for BDO, Bank Transfer, GCash, Maya, Card, Credit Card
for mop in ['BDO', 'Bank Transfer', 'GCash', 'Maya', 'Card', 'Credit Card']:
    r_mop = opener.open('http://38.247.138.224:10017/api/resource/Mode%20of%20Payment/' + urllib.parse.quote(mop))
    backup['mop_' + mop.lower().replace(' ', '_')] = json.loads(r_mop.read().decode())['data']

with open('c:/Users/josem/erpnext-system/vps_migration/backups/vehicle_sidebar_mop_backup.json', 'w', encoding='utf-8') as f:
    json.dump(backup, f, indent=2)

print('1. BACKUP complete: vehicle_sidebar_mop_backup.json')

# ============================================================
# STEP 2: Create Workspace Sidebar for Vehicle Management
# ============================================================
sidebar_data = {
    'doctype': 'Workspace Sidebar',
    'name': 'Vehicle Management',
    'title': 'Vehicle Management',
    'for_user': '',
    'items': [
        {'doctype': 'Workspace Sidebar Items', 'label': 'Customer Vehicles', 'item_type': 'Link', 'link_type': 'DocType', 'link_to': 'Customer Vehicle', 'icon': 'car', 'is_query_report': 0},
        {'doctype': 'Workspace Sidebar Items', 'label': 'Vehicle Job Orders', 'item_type': 'Link', 'link_type': 'DocType', 'link_to': 'Vehicle Job Order', 'icon': 'tool', 'is_query_report': 0},
        {'doctype': 'Workspace Sidebar Items', 'label': 'Vehicle Inspections', 'item_type': 'Link', 'link_type': 'DocType', 'link_to': 'Vehicle Inspection', 'icon': 'search', 'is_query_report': 0},
        {'doctype': 'Workspace Sidebar Items', 'label': 'Vehicle POS Invoices', 'item_type': 'Link', 'link_type': 'DocType', 'link_to': 'Vehicle POS Invoice', 'icon': 'file', 'is_query_report': 0},
        {'doctype': 'Workspace Sidebar Items', 'label': 'Vehicle Estimates', 'item_type': 'Link', 'link_type': 'DocType', 'link_to': 'Vehicle Estimate', 'icon': 'file-text', 'is_query_report': 0},
    ]
}

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Workspace%20Sidebar',
    data=json.dumps(sidebar_data).encode(),
    headers={'Content-Type': 'application/json'}
)
try:
    r3 = opener.open(req)
    created = json.loads(r3.read().decode())
    print('2. Created Vehicle Management Workspace Sidebar: HTTP', r3.status)
except urllib.error.HTTPError as e:
    err = e.read().decode()
    if 'DuplicateEntryError' in err:
        print('2. Vehicle Management Workspace Sidebar already exists, skipping.')
    else:
        print('2. ERROR creating sidebar:', e.code, err[:500])

# ============================================================
# STEP 3: Fix Mode of Payment - add missing company accounts
# ============================================================
# Get available bank accounts per company
# Use Cash accounts from Cash MoP since most companies have it configured
# For companies missing BDO/Bank Transfer, we'll add a generic Cash bank account

# Mapping of company -> their known Cash account
company_cash_accounts = {
    'Ultra MRF Mexico Warehouse': 'Cash - MEXWH',
    'Ultra MRF Warehouse Dau': 'Cash - UMDW',
    'Ultra MRF San Fernando': 'Cash - UMSF',
    'Ultra MRF Telebastagan': 'Cash - UMTEL',
    'Ultra MRF Telebastagan 2': 'Cash - UMTEL2',
    'My Company': 'Cash - MC',
    'Wheel Core': 'Cash - WCORE',
    'The Wheelhub': 'Cash - WHUB',
    'Automan Car Care Center': 'Cash - AUTOMAN',
    'San Fernando Warehouse': 'Cash - SFWH',
}

# For bank payments, we need bank accounts, not cash accounts
# Let's check what bank accounts exist for these companies
r_accts = opener.open('http://38.247.138.224:10017/api/resource/Account?limit_page_length=500&filters=[[%22account_type%22,%22=%22,%22Bank%22],[%22is_group%22,%22=%22,0]]&fields=[%22name%22,%22company%22,%22account_name%22]')
bank_accts = json.loads(r_accts.read().decode())['data']
print('3. Bank accounts found:', len(bank_accts))
for ba in bank_accts:
    print('   ', ba['company'], '->', ba['name'])
