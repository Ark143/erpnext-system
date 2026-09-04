import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

# Let's check if we can update the dashboard data via hooks or server script or DocType
# Let's test calling get_open_count on Vehicle Job Order JO-2026-00204
body = urllib.parse.urlencode({
    'doctype': 'Vehicle Job Order',
    'name': 'JO-2026-00204',
    'items': json.dumps(['Vehicle Estimate', 'Sales Invoice', 'Sales Order', 'Quotation', 'Customer Vehicle', 'Customer'])
}).encode()

try:
    res = op.open(urllib.request.Request(f'{URL}/api/method/frappe.desk.notifications.get_open_count', data=body, headers=H))
    print("Direct response:", res.read().decode())
except urllib.error.HTTPError as e:
    print("Error before fix:", e.code)
