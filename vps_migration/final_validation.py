import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

print("=== FINAL VALIDATION SUITE ===")

# 1. Check Workspace Sidebar Doc
res_sb = op.open(urllib.request.Request(f'{URL}/api/resource/Workspace%20Sidebar/Vehicle%20Management', headers=H))
sb = json.loads(res_sb.read().decode()).get('data', {})
items = sb.get('items', [])
print(f"[TEST 1] Workspace Sidebar Items: {len(items)} items")
assert len(items) >= 45, f"Expected >= 45 items, found {len(items)}"
sections = [it['label'] for it in items if it.get('type') == 'Section Break']
print(f"         Sections: {', '.join(sections)}")

# 2. Check Workspace Doc
res_ws = op.open(urllib.request.Request(f'{URL}/api/resource/Workspace/Vehicle%20Management', headers=H))
ws = json.loads(res_ws.read().decode()).get('data', {})
ncs = ws.get('number_cards', [])
charts = ws.get('charts', [])
shortcuts = ws.get('shortcuts', [])
cards = ws.get('links', [])
content = json.loads(ws.get('content', '[]'))

print(f"[TEST 2] Workspace 'Vehicle Management':")
print(f"         - Number Cards: {len(ncs)} (Expected: 7)")
print(f"         - Dashboard Charts: {len(charts)} (Expected: 16)")
print(f"         - Shortcuts: {len(shortcuts)} (Expected: 16)")
print(f"         - Card Links: {len(cards)} (Expected: 0 - cards removed)")
assert len(ncs) == 7, f"Expected 7 number cards, found {len(ncs)}"
assert len(charts) == 16, f"Expected 16 charts, found {len(charts)}"
assert len(shortcuts) == 16, f"Expected 16 shortcuts, found {len(shortcuts)}"
assert len(cards) == 0, f"Expected 0 card links, found {len(cards)}"

# 3. Check Desktop Icons
res_di = op.open(urllib.request.Request(f'{URL}/api/resource/Desktop%20Icon?limit_page_length=50', headers=H))
di_list = json.loads(res_di.read().decode()).get('data', [])
di_names = [d['name'] for d in di_list]
print(f"[TEST 3] Desktop Icons Verified ({len(di_names)} total):")
for target in ['Accounting', 'Vehicle Management', 'Invoicing', 'Financial Reports', 'Stock', 'Selling', 'Buying']:
    assert target in di_names, f"Desktop Icon '{target}' missing!"
    print(f"         - {target}: OK")

# 4. Check Key Report Accessibility
sample_reports = [
    'Monthly Sales Report',
    'Detailed Sales Report',
    'Sales Analytics',
    'Purchase Analytics',
    'Stock Balance',
    'Warehouse Wise Stock Balance',
    'Monthly Job Orders',
    'General Ledger'
]
print(f"[TEST 4] Critical Analytical Reports:")
for r in sample_reports:
    res_r = op.open(urllib.request.Request(f"{URL}/api/resource/Report/{urllib.parse.quote(r)}", headers=H))
    rdoc = json.loads(res_r.read().decode()).get('data', {})
    print(f"         - {r}: OK (Type: {rdoc.get('report_type')})")

print("\n>>> ALL VALIDATION TESTS PASSED 100% SUCCESSFULLY! <<<")
