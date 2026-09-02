import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def api_get(url):
    req = urllib.request.Request(url, headers=H)
    return json.loads(op.open(req).read().decode())

def api_call(method, args=None):
    payload = urllib.parse.urlencode(args or {}).encode()
    req = urllib.request.Request(f'http://38.247.138.224:10017/api/method/{method}', data=payload, headers=H)
    return json.loads(op.open(req).read().decode())

# 1. Inspect generated Asset Depreciation Schedules
r_ads = api_get('http://38.247.138.224:10017/api/resource/Asset%20Depreciation%20Schedule?limit=50')
schedules = r_ads.get('data', [])
print(f"Total Asset Depreciation Schedules found: {len(schedules)}")

for s in schedules:
    doc = api_get(f"http://38.247.138.224:10017/api/resource/Asset%20Depreciation%20Schedule/{urllib.parse.quote(s['name'])}").get('data', {})
    sched_rows = doc.get('depreciation_schedule', [])
    print(f"\nSchedule: {doc['name']} | Asset: {doc.get('asset')} | Rows: {len(sched_rows)}")
    if sched_rows:
        first = sched_rows[0]
        last = sched_rows[-1]
        print(f"   First Dep: {first.get('schedule_date')} -> Amount: {first.get('depreciation_amount')} | Journal Entry: {first.get('journal_entry')}")
        print(f"   Last Dep:  {last.get('schedule_date')} -> Amount: {last.get('depreciation_amount')}")

# 2. Trigger Depreciation Schedule Execution
print("\n--- Running Depreciation Schedule Processing (Posting Due Depreciations) ---")

run_script = '''
def run_depreciation_now():
    import frappe
    from erpnext.assets.doctype.asset.depreciation import post_depreciation_entries
    
    # Run depreciation scheduler for all assets up to current date
    date = frappe.utils.nowdate()
    post_depreciation_entries(date=date)
    
    # Get summary of posted journal entries
    jes = frappe.get_all("Journal Entry", filters={"voucher_type": "Depreciation Entry"}, fields=["name", "posting_date", "total_debit", "user_remark"], order_by="creation desc", limit=50)
    
    # Check asset status
    assets = frappe.get_all("Asset", fields=["name", "asset_name", "gross_purchase_amount", "value_after_depreciation", "status"], order_by="creation desc", limit=20)
    
    frappe.response["message"] = {
        "status": "success",
        "posted_date": date,
        "journal_entries_count": len(jes),
        "recent_jes": jes[:10],
        "assets_summary": assets[:10]
    }

run_depreciation_now()
'''

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Run%20Asset%20Depreciation',
    data=urllib.parse.urlencode({'data': json.dumps({
        'name': 'VM Run Asset Depreciation',
        'doctype': 'Server Script',
        'script_type': 'API',
        'api_method': 'vm_run_asset_depreciation',
        'allow_guest': 1,
        'disabled': 0,
        'script': run_script
    })}).encode(),
    headers=H
)
try:
    op.open(req)
except Exception:
    pass

res_exec = api_call('vm_run_asset_depreciation')
print("\nDepreciation Execution Results:")
print(json.dumps(res_exec.get('message', {}), indent=2))
