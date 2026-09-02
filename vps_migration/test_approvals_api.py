import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

# Test executive_dashboard approvals view
r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vehicle_management.vehicle_management.vehicle_management.executive_dashboard.executive_dashboard?view=approvals&company=ULTRA%20MRF', headers=H))
res = json.loads(r.read().decode())
print("Approvals result:")
for c in res.get('message', []):
    if c['count'] > 0:
        print(f"  DocType: {c['doctype']} | Count: {c['count']} | Total: PHP {c['total']}")
        for it in c.get('items', []):
            print(f"    - {it['name']} | PHP {it['amount']} | {it['date']}")
