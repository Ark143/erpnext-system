import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

res = op.open(urllib.request.Request(f"{URL}/api/resource/Workspace/Vehicle%20Management", headers=H))
ws = json.loads(res.read().decode()).get('data', {})

print("=== TESTING ALL WORKSPACE CHARTS ===")
for c in ws.get('charts', []):
    cname = c.get('chart_name')
    chart_req = urllib.parse.urlencode({
        'chart_name': cname,
        'refresh': 1
    }).encode()
    try:
        res_c = op.open(urllib.request.Request(f"{URL}/api/method/frappe.desk.doctype.dashboard_chart.dashboard_chart.get", data=chart_req, headers=H))
        cdata = json.loads(res_c.read().decode())
        print(f"[PASS] {cname}: OK")
    except Exception as e:
        print(f"[FAIL] {cname}: {e}")
