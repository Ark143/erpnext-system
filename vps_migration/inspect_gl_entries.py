import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def api_get(url):
    req = urllib.request.Request(url, headers=H)
    return json.loads(op.open(req).read().decode())

qs = urllib.parse.urlencode({
    'filters': json.dumps([['voucher_type', '=', 'POS Invoice']]),
    'fields': json.dumps(['name', 'voucher_no', 'posting_date', 'account', 'debit', 'credit', 'is_cancelled']),
    'limit': 100
})
gles = api_get(f'http://38.247.138.224:10017/api/resource/GL%20Entry?{qs}').get('data', [])
print(f"Total GL Entries created by POS Invoices: {len(gles)}")
for gl in gles:
    debit = float(gl.get('debit', 0))
    credit = float(gl.get('credit', 0))
    cancelled = " (CANCELLED)" if gl.get('is_cancelled') else ""
    print(f"  {gl['voucher_no']} | Date: {gl['posting_date']} | Account: {gl['account']} | Debit: PHP {debit:,.2f} | Credit: PHP {credit:,.2f}{cancelled}")
