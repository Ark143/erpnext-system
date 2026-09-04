import urllib.request, urllib.parse, json, http.cookiejar, re

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type':'application/x-www-form-urlencoded','X-Requested-With':'XMLHttpRequest','Accept':'application/json'}
data = urllib.parse.urlencode({'cmd':'login','usr':'administrator','pwd':'admin'}).encode()
op.open(urllib.request.Request(URL+'/api/method/login', data=data, headers=H), timeout=30)
r = op.open(urllib.request.Request(URL+'/app', headers=H), timeout=60)
html = r.read().decode('utf-8', 'ignore')
m = re.search(r'frappe\.boot\s*=\s*(\{.*?\});', html, re.DOTALL)
boot = json.loads(m.group(1))

items = boot.get('workspace_sidebar_item', {}).get('vehicle management', {}).get('items', [])
print(f"Total items in vehicle management sidebar: {len(items)}")
for i, it in enumerate(items):
    print(f"{i+1:02d}. [{it.get('type')}] {it.get('label')} -> {it.get('link_type')}: {it.get('link_to')}")

print("\n--- ALL DESKTOP ICONS ---")
for it in boot.get('desktop_icons', []):
    print(f"Icon: {it.get('label')} | link_type: {it.get('link_type')} | link_to: {it.get('link_to')} | sidebar: {it.get('sidebar')}")

print("\n--- ALL WORKSPACES IN BOOT ---")
for p in boot.get('workspaces', {}).get('pages', []):
    print(f"Workspace: {p.get('name')} | title: {p.get('title')} | parent_page: {p.get('parent_page')}")
