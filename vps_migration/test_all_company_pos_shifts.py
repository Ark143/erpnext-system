"""Test the POS shift-opening flow for EVERY company on the VPS demo.

For each non-group company with a 'Vehicle POS - {Company}' profile:
  1. Resolve its POS profile + warehouse, and check warehouse<->company match.
  2. Open a real shift (vm_pos_open_shift) as Administrator.
  3. Verify the POS Opening Entry was created (HTTP 200, name returned).
  4. Cancel the entry so no open shift is left behind.
Prints a per-company table + a summary of failures.
"""
import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://38.247.138.224:10017'
CASHIER = 'Administrator'  # real user (link field to User must exist)

s = requests.Session()
r = s.post(f'{BASE}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)
assert r.status_code == 200, f'login failed {r.status_code}'

# 1. Companies (non-group) + profiles from the same source the frontend uses
meta = s.get(f'{BASE}/api/method/vm_pos_get_shift',
             params={'user': CASHIER, 'company': 'ULTRA MRF'}, timeout=30).json().get('message', {})
companies = meta.get('companies', [])
profiles = meta.get('profiles', [])

prof_by_co = {}
for p in profiles:
    prof_by_co.setdefault(p['company'], []).append(p)

print(f"Companies (non-group): {len(companies)}")
print(f"POS Profiles in meta:  {len(profiles)}")
print("=" * 78)

results = []
for co in companies:
    profs = prof_by_co.get(co, [])
    canon = [p for p in profs if p['name'] == f'Vehicle POS - {co}'] or profs
    if not canon:
        results.append((co, 'NO PROFILE', '', '', 'FAIL'))
        print(f"[FAIL] {co}: no POS profile in meta")
        continue

    prof = canon[0]
    pname = prof['name']
    wh = prof.get('warehouse') or ''

    # warehouse<->company consistency check
    wh_company = ''
    if wh:
        try:
            whd = s.get(f"{BASE}/api/resource/Warehouse/{requests.utils.quote(wh)}", timeout=30).json()['data']
            wh_company = whd.get('company') or ''
        except Exception:
            wh_company = '?'

    # 2. Open a real shift
    payload = json.dumps({
        'company': co,
        'pos_profile': pname,
        'opening_amount': 500.00,
        'mode_of_payment': 'Cash',
        'user': CASHIER,
    })
    try:
        rr = s.post(f'{BASE}/api/method/vm_pos_open_shift', data={'data': payload}, timeout=60)
        d = rr.json()
    except Exception as e:
        results.append((co, pname, wh, wh_company, f'FAIL (transport: {e})'))
        print(f"[FAIL] {co}: {pname} -> transport error {e}")
        continue

    if 'exc' in d:
        exc = d.get('exc_type', 'Exception')
        msg = str(d.get('exc', ''))[:160].replace('\n', ' ')
        results.append((co, pname, wh, wh_company, f'FAIL ({exc})'))
        print(f"[FAIL] {co}: {pname} -> {exc}: {msg}")
        continue

    m = d.get('message', {})
    entry = m.get('name')
    status = m.get('status')

    # 3. Verify get_shift now reports it open
    recheck_ok = False
    if entry:
        try:
            g = s.get(f'{BASE}/api/method/vm_pos_get_shift',
                      params={'user': CASHIER, 'company': co}, timeout=30).json().get('message', {})
            recheck_ok = bool(g.get('has_open_shift')) and (g.get('shift') or {}).get('name') == entry
        except Exception:
            recheck_ok = False

    # 4. Cancel to leave no open shift
    cancelled = False
    if entry:
        try:
            cr = s.post(f'{BASE}/api/method/frappe.client.cancel',
                        data={'doctype': 'POS Opening Entry', 'name': entry}, timeout=60)
            cancelled = cr.json().get('message', {}).get('docstatus') == 2
        except Exception:
            cancelled = False

    wh_flag = 'OK' if (wh_company == co) else f'WARN(wh={wh_company})'
    ok = bool(entry) and recheck_ok and cancelled
    results.append((co, pname, wh, wh_flag, 'OK' if ok else 'PARTIAL'))
    tag = 'OK ' if ok else '???'
    print(f"[{tag}] {co}: {pname}")
    print(f"       wh={wh or '(none)'} [{wh_flag}]  entry={entry}  recheck_open={recheck_ok}  cancelled={cancelled}")

print("=" * 78)
fails = [r for r in results if not r[4].startswith('OK')]
print(f"TOTAL: {len(results)} companies tested | OK={len(results)-len(fails)} | problems={len(fails)}")
for r in fails:
    print("  PROBLEM:", r)
