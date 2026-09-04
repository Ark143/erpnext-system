import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(URL + '/api/method/login', data=data, headers=H), timeout=30)

body = urllib.parse.urlencode({
    'report_name': 'Item-wise Sales History',
    'filters': json.dumps({'from_date': '2026-08-03', 'to_date': '2026-09-03'}),
    'ignore_prepared_report': 1
}).encode()

try:
    res = op.open(urllib.request.Request(URL + '/api/method/frappe.desk.query_report.run', data=body, headers=H))
    print("Report result:", res.read().decode()[:500])
except Exception as e:
    print("Report failed as expected:", e)
