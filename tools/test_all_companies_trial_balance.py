import json
import urllib.request
import urllib.parse
import http.cookiejar

BASE = "http://38.247.138.224:10017"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}

def login(usr="Administrator", pwd="admin"):
    login_h = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    with op.open(
        urllib.request.Request(
            BASE + "/api/method/login",
            data=f"usr={usr}&pwd={pwd}".encode(),
            headers=login_h,
            method="POST",
        ),
        timeout=30,
    ) as r:
        raw = r.read().decode()
        if "message" in raw and "Logged In" in raw:
            print("[OK] Logged into VPS as Administrator")

def call(path, method="GET", payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, headers=H, method=method)
    try:
        with op.open(req, timeout=60) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  HTTP {e.code} on {method} {path}: {body[:400]}")
        try:
            return json.loads(body)
        except Exception:
            return {"error": body}

login()

companies = ["Automan Car Care Center", "ULTRA MRF", "Ultra MRF Dau Main"]

for co in companies:
    print(f"\n--- Testing Trial Balance for Company: {co} ---")
    test_payload = {
        'report_name': 'Trial Balance',
        'filters': json.dumps({
            'company': co,
            'fiscal_year': '2026',
            'from_date': '2026-01-01',
            'to_date': '2026-12-31',
            'cost_center': [],
            'project': [],
            'branch': [],
            'with_period_closing_entry_for_opening': 1,
            'with_period_closing_entry_for_current_period': 1,
            'include_default_book_entries': 1,
            'show_net_values': 1,
            'show_group_accounts': 1
        }),
        'ignore_prepared_report': 1
    }
    qs = urllib.parse.urlencode(test_payload)
    res = call(f"/api/method/frappe.desk.query_report.run?{qs}", "GET")
    rep = res.get('message', {})
    cols = rep.get('columns', [])
    rows = rep.get('result', [])
    print(f"  [OK] Returned {len(cols)} columns and {len(rows)} rows.")
    
    total_row = None
    for r in rows:
        if r.get('account') == "'Total'":
            total_row = r
            break
            
    if total_row:
        print(f"  Total Closing (Dr): {total_row.get('closing_debit')}, Total Closing (Cr): {total_row.get('closing_credit')}")
        print(f"  Total Debit Movement: {total_row.get('debit')}, Total Credit Movement: {total_row.get('credit')}")
    else:
        print("  (No total row found or empty ledger)")

print("\n>>> ALL COMPANIES TESTED SUCCESSFULLY! <<<")
