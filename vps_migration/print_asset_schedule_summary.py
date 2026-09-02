import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def api_get(url):
    req = urllib.request.Request(url, headers=H)
    return json.loads(op.open(req).read().decode())

print("="*95)
print("                           10 CREATED & SUBMITTED FIXED ASSETS")
print("="*95)

r_assets = api_get('http://38.247.138.224:10017/api/resource/Asset?limit=20')
asset_list = r_assets.get('data', [])

for i, a_ref in enumerate(asset_list[:10], 1):
    a = api_get(f"http://38.247.138.224:10017/api/resource/Asset/{urllib.parse.quote(a_ref['name'])}").get('data', {})
    cost = float(a.get('gross_purchase_amount') or 0)
    print(f"{i:2d}. [{a['name']}] {a.get('asset_name')}")
    print(f"    Item Code : {a.get('item_code')} | Category: {a.get('asset_category')}")
    print(f"    Company   : {a.get('company')} | Location: {a.get('location', 'N/A')}")
    print(f"    Cost      : PHP {cost:,.2f} | Status: {a.get('status')} | Docstatus: {a.get('docstatus')}")
    print("-" * 95)

print("\n" + "="*95)
print("                           10 GENERATED DEPRECIATION SCHEDULES")
print("="*95)

r_schedules = api_get('http://38.247.138.224:10017/api/resource/Asset%20Depreciation%20Schedule?limit=20')
sched_list = r_schedules.get('data', [])

for i, s_ref in enumerate(sched_list[:10], 1):
    doc = api_get(f"http://38.247.138.224:10017/api/resource/Asset%20Depreciation%20Schedule/{urllib.parse.quote(s_ref['name'])}").get('data', {})
    rows = doc.get('depreciation_schedule', [])
    first_row = rows[0] if rows else {}
    last_row = rows[-1] if rows else {}
    monthly_dep = float(first_row.get('depreciation_amount') or 0)
    
    print(f"{i:2d}. Schedule ID: {doc.get('name')} -> For Asset: {doc.get('asset')}")
    print(f"    Method      : {doc.get('depreciation_method', 'Straight Line')} | Frequency: {doc.get('frequency_of_depreciation', 1)} Month(s)")
    print(f"    Schedule    : {len(rows)} Periods ({first_row.get('schedule_date')} to {last_row.get('schedule_date')})")
    print(f"    Monthly Dep : PHP {monthly_dep:,.2f} / month | Status: {doc.get('status', 'Active')}")
    print("-" * 95)
