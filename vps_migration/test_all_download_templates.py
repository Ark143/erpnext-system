import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

r_dt = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/DocType?filters=[[\"istable\",\"=\",0],[\"issingle\",\"=\",0]]&limit=500', headers=H))
doctypes = [d['name'] for d in json.loads(r_dt.read().decode())['data']]
print(f"Testing {len(doctypes)} DocTypes with download_template...")

failing_doctypes = []

for dt in doctypes:
    qs = urllib.parse.urlencode({
        'doctype': dt,
        'export_fields': json.dumps({}),
        'export_data': '0'
    })
    try:
        r = op.open(urllib.request.Request(f'http://38.247.138.224:10017/api/method/frappe.core.doctype.data_import.data_import.download_template?{qs}', headers=H))
        # print(f"OK: {dt}")
    except urllib.error.HTTPError as e:
        err = e.fp.read().decode('utf-8', 'ignore') if e.fp else ""
        if "Value for" in err or "cannot be a list" in err:
            print(f"FAILED on DocType '{dt}': {err[:300]}")
            failing_doctypes.append((dt, err))
        else:
            # other error (permissions or missing file)
            pass

print(f"\nTotal failing DocTypes with 'cannot be a list': {len(failing_doctypes)}")
for dt, err in failing_doctypes:
    print(f"- {dt}")
