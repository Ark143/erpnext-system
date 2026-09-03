import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# Get "Home" sidebar - likely where top-level workspaces are listed
r = opener.open('http://38.247.138.224:10017/api/resource/Workspace%20Sidebar/Home')
home = json.loads(r.read().decode())['data']
print('Home sidebar items:')
for it in home.get('items', []):
    print(' ', it.get('label'), '->', it.get('link_to'), 'icon:', it.get('icon'), 'item_type:', it.get('item_type'))

print()
# Also check if there's a "parent_page" approach for Vehicle Management in workspaces
# Look for items that reference Vehicle Management
r2 = opener.open('http://38.247.138.224:10017/api/resource/Workspace?limit_page_length=100&fields=[\"name\",\"parent_page\",\"icon\"]')
ws_list = json.loads(r2.read().decode())['data']
print('Workspaces with Vehicle in name or parent:', [(w['name'], w.get('parent_page'), w.get('icon')) for w in ws_list if 'vehicle' in w['name'].lower() or 'Vehicle' in str(w.get('parent_page', ''))])
