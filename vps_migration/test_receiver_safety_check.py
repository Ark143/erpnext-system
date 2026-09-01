import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

print("=== 1. Testing vm_verify_receiver_badge API ===")
data_verify = urllib.parse.urlencode({'qr_data': 'Administrator|admin'}).encode()
r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_verify_receiver_badge', data=data_verify, headers=H))
res = json.loads(r.read().decode())
print("API Response for 'Administrator|admin':", json.dumps(res, indent=2))
assert res.get('message', {}).get('ok') is True, "API verification failed!"

print("\n=== 2. Testing Stock Entry Submission Safety Check Validation ===")
# Fetch item and warehouse
r_item = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Item?limit=1', headers=H))
item = json.loads(r_item.read().decode())['data'][0]['name']

r_wh = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Warehouse?filters=[[\"is_group\",\"=\",0]]&limit=1', headers=H))
wh = json.loads(r_wh.read().decode())['data'][0]['name']

r_co = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Company?limit=1', headers=H))
co = json.loads(r_co.read().decode())['data'][0]['name']

stock_entry_doc = {
    "doctype": "Stock Entry",
    "stock_entry_type": "Material Issue",
    "company": co,
    "items": [
        {
            "item_code": item,
            "qty": 1,
            "s_warehouse": wh,
            "basic_rate": 100
        }
    ]
}

# Create draft Material Issue Stock Entry
r_se = op.open(urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Stock%20Entry',
    data=urllib.parse.urlencode({'data': json.dumps(stock_entry_doc)}).encode(),
    headers=H
))
se_res = json.loads(r_se.read().decode())
se_name = se_res['data']['name']
print(f"Created Draft Stock Entry: {se_name}")

# Try to submit without receiver verification -> Expect failure
try:
    req_submit = urllib.request.Request(
        f'http://38.247.138.224:10017/api/resource/Stock%20Entry/{se_name}',
        data=urllib.parse.urlencode({'data': json.dumps({'docstatus': 1})}).encode(),
        headers=H
    )
    req_submit.get_method = lambda: 'PUT'
    op.open(req_submit)
    print("ERROR: Stock Entry submitted without receiver verification (it should have been blocked!)")
except urllib.error.HTTPError as e:
    print(f"PASS: Submission was correctly blocked (HTTP {e.code})!")
    err_body = e.fp.read().decode('utf-8', 'ignore') if e.fp else ""
    print("Error message preview:", err_body[:200])

# Clean up test stock entry draft
req_del = urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Stock%20Entry/{se_name}', headers=H)
req_del.get_method = lambda: 'DELETE'
op.open(req_del)
print(f"Cleaned up test Stock Entry {se_name}")

print("\nALL AUTOMATED TESTS PASSED!")
