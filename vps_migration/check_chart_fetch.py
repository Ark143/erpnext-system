import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

# Check Dashboard Chart
res = op.open(urllib.request.Request(f"{URL}/api/resource/Dashboard%20Chart/Item-wise%20Annual%20Sales", headers=H))
chart_doc = json.loads(res.read().decode()).get('data', {})
print("Item-wise Annual Sales filters_json:", chart_doc.get('filters_json'))
print("Item-wise Annual Sales dynamic_filters_json:", chart_doc.get('dynamic_filters_json'))

# Test chart fetch via desk endpoint
chart_req = urllib.parse.urlencode({
    'chart_name': 'Item-wise Annual Sales',
    'refresh': 1
}).encode()
res_c = op.open(urllib.request.Request(f"{URL}/api/method/frappe.desk.doctype.dashboard_chart.dashboard_chart.get", data=chart_req, headers=H))
print("Chart fetch response status:", res_c.getcode())
cdata = json.loads(res_c.read().decode()).get('message', {})
print("Chart dataset labels:", cdata.get('labels', [])[:5])
