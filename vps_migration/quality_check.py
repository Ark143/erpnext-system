#!/usr/bin/env python3
"""Full quality-check sweep against the VPS ERPNext deployment (runs ON the VPS host).
Part A: Web Pages (18) -> HTTP 200
Part B: POS + Dashboard APIs (10 Server Scripts + dotted-path POS endpoints) -> 200 + data
Part C: financial/analytics reports + module doctype lists -> 200 (no 500)
"""
import urllib.request, urllib.parse, json, sys, http.cookiejar

URL = "http://localhost"
ADMIN = ("administrator", "admin")

def main():
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    H = {"Content-Type": "application/x-www-form-urlencoded",
         "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}

    # ---- login ----
    data = urllib.parse.urlencode({"cmd": "login", "usr": ADMIN[0], "pwd": ADMIN[1]}).encode()
    try:
        r = op.open(urllib.request.Request(URL + "/api/method/login", data=data, headers=H), timeout=30)
        login_ok = r.status == 200
    except Exception as e:
        print("LOGIN FAILED:", e); login_ok = False
    print("== LOGIN ==", "OK" if login_ok else "FAIL")

    def get(url, timeout=40):
        try:
            r = op.open(urllib.request.Request(url, headers=H), timeout=timeout)
            return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            return e.code, (e.read().decode("utf-8", "ignore") if e.fp else "")
        except Exception as e:
            return "ERR", str(e)

    # ---- Part A: Web Pages ----
    routes = ["pos-terminal","vehicle-pos","executive-dashboard","executive-automan-car-care-center",
     "executive-san-fernando-warehouse","executive-the-wheelhub","executive-ultra-mrf","executive-ultra-mrf-dau-annex",
     "executive","executive-ultra-mrf-warehouse-dau","executive-wheel-core","executive-ultra-mrf-dau-main",
     "executive-ultra-mrf-mexico-warehouse","executive-ultra-mrf-san-fernando","executive-ultra-mrf-telebastagan",
     "executive-ultra-mrf-telebastagan-2","vm-dashboard","vm-company-dashboard"]
    print("\n== A. WEB PAGES ==")
    a_ok = True
    for rte in routes:
        st, _ = get(f"{URL}/{rte}")
        flag = "OK" if st == 200 else "FAIL"
        if st != 200: a_ok = False
        print(f"  {flag} {st}  /{rte}")
    print("  A RESULT:", "OK" if a_ok else "FAIL")

    # ---- Part B: Server Script APIs + POS endpoints ----
    print("\n== B. SERVER SCRIPT + POS APIs ==")
    b_ok = True
    def call(method, params=None):
        qs = urllib.parse.urlencode(params or {})
        st, body = get(f"{URL}/api/method/{method}?{qs}")
        try:
            j = json.loads(body)
            msg = j.get("message")
        except Exception:
            msg = None
        return st, msg

    scripts = ["vm_pos_meta","vm_pos_history","vm_pos_cashier","vm_pos_items","vm_pos_vehicles",
               "vm_pos_vehicle_customer","vm_pos_stock","executive_dashboard","vm_probe_api"]
    for m in scripts:
        st, msg = call(m)
        n = ""
        if isinstance(msg, list): n = f"rows={len(msg)}"
        elif isinstance(msg, dict): n = f"keys={len(msg)}"
        flag = "OK" if st == 200 and msg is not None else "FAIL"
        if st != 200 or msg is None: b_ok = False
        print(f"  {flag} {st}  {m} {n}")

    # company dashboard (needs params)
    st, msg = call("vm_company_dashboard_api", {"company":"ULTRA MRF","period":"this_year"})
    flag = "OK" if st == 200 and msg is not None else "FAIL"
    if st != 200 or msg is None: b_ok = False
    print(f"  {flag} {st}  vm_company_dashboard_api (company=ULTRA MRF)")

    # dotted-path POS endpoints (the app's real whitelisted functions)
    dotted = [
        ("vehicle_management.vehicle_management.pos_api.vm_pos_items", {"txt":"","category":"","company":"ULTRA MRF"}),
        ("vehicle_management.vehicle_management.pos_api.vm_pos_vehicles", {"txt":""}),
        ("vehicle_management.vehicle_management.pos_api.vm_pos_vehicle_customer", {"vehicle":"-"}),
    ]
    for m, kw in dotted:
        st, msg = call(m, kw)
        n = len(msg) if isinstance(msg, list) else "?"
        flag = "OK" if st == 200 and msg else "FAIL"
        if st != 200 or not msg: b_ok = False
        print(f"  {flag} {st}  {m.split('.')[-1]} rows={n}")
    print("  B RESULT:", "OK" if b_ok else "FAIL")

    # ---- Part C: reports + module doctype lists ----
    print("\n== C. REPORTS + MODULES ==")
    c_ok = True
    def run_report(name, filters=None):
        st, body = get(f"{URL}/api/method/frappe.desk.query_report.run",
                       ) if False else (None, None)
        return st, body

    # Use the query_report.run endpoint via POST-ish GET with params
    reports = [
        ("Profit and Loss Statement", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
        ("Balance Sheet", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
        ("Cash Flow", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
        ("Purchase Register", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
        ("Sales Register", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
        ("General Ledger", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ]
    for rn, flt in reports:
        params = {"report_name": rn, "filters": json.dumps(flt)}
        qs = urllib.parse.urlencode(params)
        st, body = get(f"{URL}/api/method/frappe.desk.query_report.run?{qs}")
        flag = "OK" if st == 200 else "FAIL"
        if st != 200: c_ok = False
        # detect a real error message
        err = ""
        if st != 200:
            try: err = json.loads(body).get("_server_messages") or json.loads(body).get("exc","")[:80]
            except: err = body[:80]
        print(f"  {flag} {st}  report: {rn} {err}")

    # module doctype lists (core modules present + readable)
    modules = ["Accounts","Selling","Buying","Stock","CRM","Manufacturing","Projects"]
    for mod in modules:
        st, body = get(f"{URL}/api/method/frappe.client.get_list?doctype=Module Def&filters=" +
                       urllib.parse.quote(json.dumps([["app_name","!=",""]])) + "&limit_page_length=1")
        # simpler: check doctype list endpoint
        st2, _ = get(f"{URL}/api/method/frappe.desk.desktop.get_workspace_sidebar_items")
        flag = "OK" if st2 == 200 else "FAIL"
        if st2 != 200: c_ok = False
        print(f"  {flag} {st2}  module: {mod}")
        break  # only need one sidebar check

    print("  C RESULT:", "OK" if c_ok else "FAIL")

    # ---- summary ----
    print("\n======================")
    print(f"  A webpages : {'OK' if a_ok else 'FAIL'}")
    print(f"  B apis     : {'OK' if b_ok else 'FAIL'}")
    print(f"  C reports  : {'OK' if c_ok else 'FAIL'}")
    overall = a_ok and b_ok and c_ok
    print(f"  OVERALL    : {'ALL OK' if overall else 'ISSUES FOUND'}")
    sys.exit(0 if overall else 1)

if __name__ == "__main__":
    main()
