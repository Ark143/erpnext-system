#!/usr/bin/env python3
"""Re-check the 3 date-based reports with correct filter keys, and module doctypes."""
import urllib.request, urllib.parse, json, sys, http.cookiejar

URL = "http://localhost"
def main():
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    H = {"Content-Type": "application/x-www-form-urlencoded",
         "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}
    data = urllib.parse.urlencode({"cmd":"login","usr":"administrator","pwd":"admin"}).encode()
    op.open(urllib.request.Request(URL+"/api/method/login", data=data, headers=H), timeout=30)
    def get(url):
        try:
            r = op.open(urllib.request.Request(url, headers=H), timeout=40)
            return r.status, r.read().decode("utf-8","ignore")
        except urllib.error.HTTPError as e:
            return e.code, (e.read().decode() if e.fp else "")
        except Exception as e:
            return "ERR", str(e)

    print("== date-based reports (correct filters) ==")
    reports = [
        ("Profit and Loss Statement", {"company":"ULTRA MRF","period_start_date":"2026-01-01","period_end_date":"2026-12-31","from_date":"2026-01-01","to_date":"2026-12-31"}),
        ("Balance Sheet", {"company":"ULTRA MRF","period_start_date":"2026-01-01","period_end_date":"2026-12-31","from_date":"2026-01-01","to_date":"2026-12-31"}),
        ("Cash Flow", {"company":"ULTRA MRF","period_start_date":"2026-01-01","period_end_date":"2026-12-31","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ]
    for rn, flt in reports:
        params = {"report_name": rn, "filters": json.dumps(flt)}
        qs = urllib.parse.urlencode(params)
        st, body = get(f"{URL}/api/method/frappe.desk.query_report.run?{qs}")
        flag = "OK" if st == 200 else "FAIL"
        if st == 200:
            try:
                j = json.loads(body); n = len(j.get("message",{}).get("result",[]))
                print(f"  {flag} {st}  {rn} rows={n}")
            except Exception:
                print(f"  {flag} {st}  {rn} (parsed)")
        else:
            print(f"  {flag} {st}  {rn} :: {body[:120]}")

    print("\n== module doctype list ==")
    st, body = get(URL + "/api/method/frappe.client.get_list?doctype=Module%20Def&fields=%5B%22name%22%2C%22app_name%22%5D&limit_page_length=100")
    flag = "OK" if st == 200 else "FAIL"
    mods = []
    if st == 200:
        try:
            j = json.loads(body); mods = [m.get("name") for m in j.get("message",[])]
        except: pass
    print(f"  {flag} {st}  Module Def list, count={len(mods)}")
    print("  sample:", mods[:15])

main()
