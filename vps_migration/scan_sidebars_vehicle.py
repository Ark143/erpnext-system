import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

names = [
    'Automation', 'Build', 'Data', 'Email', 'Integrations', 'My Workspaces', 'Printing',
    'System', 'Users', 'Website', 'Accounts Setup', 'Assets', 'Banking', 'Budget', 'Buying',
    'CRM', 'ERPNext Settings', 'Financial Reports', 'Home', 'Invoicing', 'Manufacturing',
    'Organization', 'Payments', 'Projects', 'Quality', 'Selling', 'Share Management',
    'Stock', 'Subcontracting', 'Subscription', 'Support', 'Taxes', 'ERPNext Integrations', 'Utilities'
]

for name in names:
    url = 'http://38.247.138.224:10017/api/resource/Workspace%20Sidebar/' + urllib.parse.quote(name)
    sb = json.loads(opener.open(url).read().decode())['data']
    for it in sb.get('items', []):
        lt = it.get('link_to') or ''
        lb = it.get('label') or ''
        icon = it.get('icon') or ''
        if 'vehicle' in lt.lower() or 'vehicle' in lb.lower():
            print('FOUND in sidebar [' + name + ']: label=' + lb + ', link_to=' + lt + ', icon=' + icon + ', item_type=' + str(it.get('item_type')) + ', link_type=' + str(it.get('link_type')))

print('Done scanning sidebars.')

# Also check Desk Page/Shortcut doctype for Vehicle Management
r_ws = opener.open('http://38.247.138.224:10017/api/resource/Workspace/Vehicle%20Management')
ws = json.loads(r_ws.read().decode())['data']
print('Vehicle Management workspace icon:', ws.get('icon'))
print('Vehicle Management parent_page:', ws.get('parent_page'))
shortcuts = ws.get('shortcuts', [])
print('Shortcuts count:', len(shortcuts))
for sc in shortcuts[:5]:
    print(' shortcut:', sc.get('label'), '->', sc.get('link_to'), 'icon:', sc.get('icon'))
