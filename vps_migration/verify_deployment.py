import urllib.request, urllib.parse, json, http.cookiejar, re

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

r = op.open(urllib.request.Request(f'{URL}/app', headers=H), timeout=60)
html = r.read().decode('utf-8', 'ignore')
m = re.search(r'frappe\.boot\s*=\s*(\{.*?\});', html, re.DOTALL)
boot = json.loads(m.group(1))

# Check sidebar
vm_sb = boot.get('workspace_sidebar_item', {}).get('vehicle management', {}).get('items', [])
print(f"Vehicle Management Sidebar Items Count: {len(vm_sb)}")
sections = [it['label'] for it in vm_sb if it.get('type') == 'Section Break']
print("  Section breaks found:", sections)

# Check accounting desktop icon
for icon in boot.get('desktop_icons', []):
    if icon.get('label') in ['Accounting', 'Vehicle Management', 'Invoicing', 'Financial Reports']:
        print(f"  Desktop Icon '{icon.get('label')}': link_type={icon.get('link_type')}, link_to={icon.get('link_to')}")

# Check workspace doc
res_ws = op.open(urllib.request.Request(f'{URL}/api/resource/Workspace/Vehicle%20Management', headers=H))
ws_data = json.loads(res_ws.read().decode()).get('data', {})
print(f"\nWorkspace 'Vehicle Management' Summary:")
print(f"  Title: {ws_data.get('title')}")
print(f"  Number Cards count: {len(ws_data.get('number_cards', []))}")
print(f"  Charts count: {len(ws_data.get('charts', []))}")
print(f"  Shortcuts count: {len(ws_data.get('shortcuts', []))}")
print(f"  Links count (Cards): {len(ws_data.get('links', []))} (Should be 0)")

content = json.loads(ws_data.get('content', '[]'))
print(f"  Content blocks count: {len(content)}")
headers = [c['data']['text'] for c in content if c.get('type') == 'header']
print("  Headers in workspace:")
for h in headers:
    print("   -", h)
