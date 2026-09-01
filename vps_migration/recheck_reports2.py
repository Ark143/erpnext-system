#!/usr/bin/env python3
import urllib.request, urllib.parse, json, http.cookiejar
URL = "http://localhost"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {"Content-Type":"application/x-www-form-urlencoded","X-Requested-With":"XMLHttpRequest","Accept":"application/json"}
data = urllib.parse.urlencode({"cmd":"login","usr":"administrator","pwd":"admin"}).encode()
op.open(urllib.request.Request(URL+"/api/method/login", data=data, headers=H), timeout=30)
def get(url):
    try:
        r = op.open(urllib.request.Request(url, headers=H), timeout=60)
        return r.status, r.read().decode("utf-8","ignore")
    except urllib.error.HTTPError as e:
        return e.code, (e.read().decode() if e.fp else "")
    except Exception as e:
        return "ERR", str(e)

reports = [
    ("Profit and Loss Statement", {"company":"ULTRA MRF","from_fiscal_year":"2026","to_fiscal_year":"2026","filter_based_on":"Fiscal Year","periodicity":"Yearly"}),
    ("Balance Sheet", {"company":"ULTRA MRF","from_fiscal_year":"2026","to_fiscal_year":"2026","filter_based_on":"Fiscal Year","periodicity":"Yearly"}),
    ("Cash Flow", {"company":"ULTRA MRF","from_fiscal_year":"2026","to_fiscal_year":"2026","filter_based_on":"Fiscal Year","periodicity":"Yearly"}),
]
for rn, flt in reports:
    params = {"report_name": rn, "filters": json.dumps(flt)}
    qs = urllib.parse.urlencode(params)
    st, body = get(f"{URL}/api/method/frappe.desk.query_report.run?{qs}")
    if st == 200:
        try:
            j = json.loads(body); rows = j.get("message",{}).get("result",[])
            print(f"OK 200  {rn}  rows={len(rows)}")
        except Exception as e:
            print(f"OK 200  {rn}  (parse err {e})")
    else:
        print(f"FAIL {st}  {rn} :: {body[:160]}")
