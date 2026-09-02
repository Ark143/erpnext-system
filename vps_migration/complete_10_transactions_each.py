import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def api_get(url):
    req = urllib.request.Request(url, headers=H)
    return json.loads(op.open(req).read().decode())

def api_post_rpc(method, args):
    payload = urllib.parse.urlencode({'data': json.dumps(args)}).encode()
    req = urllib.request.Request(f'http://38.247.138.224:10017/api/method/{method}', data=payload, headers=H)
    return json.loads(op.open(req).read().decode()).get('message', {})

def frappe_customer_exists(cust):
    try:
        r = op.open(urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Customer/{urllib.parse.quote(cust)}', headers=H))
        return True
    except Exception:
        return False

# 1. Fetch valid Customer Vehicles
qs_v = urllib.parse.urlencode({'fields': json.dumps(['name', 'customer', 'plate_no']), 'limit': 60})
r_vehs = api_get(f'http://38.247.138.224:10017/api/resource/Customer%20Vehicle?{qs_v}').get('data', [])

verified_pairs = []
for v in r_vehs:
    c = v.get('customer')
    if c and frappe_customer_exists(c):
        verified_pairs.append({'customer': c, 'vehicle': v['name'], 'plate': v.get('plate_no') or v['name']})

print(f"Verified {len(verified_pairs)} Customer-Vehicle pairs with active Customer records.")

# 2. Fetch standard sellable items
r_items = api_get('http://38.247.138.224:10017/api/resource/Item?limit=25')
confirmed_items = []
for it in r_items.get('data', []):
    doc = api_get(f"http://38.247.138.224:10017/api/resource/Item/{urllib.parse.quote(it['name'])}").get('data', {})
    rate = float(doc.get('standard_rate') or 200.0)
    if rate <= 0: rate = 150.0
    confirmed_items.append({'item_code': doc['name'], 'rate': rate, 'uom': doc.get('stock_uom') or 'Nos'})

target_companies = [
    "ULTRA MRF",
    "Ultra MRF Dau Main",
    "Ultra MRF Dau Annex"
]

# Check existing successful transactions per company
for comp in target_companies:
    qs = urllib.parse.urlencode({
        'filters': json.dumps([['company', '=', comp], ['docstatus', '=', 1], ['pos_invoice', '!=', '']]),
        'fields': json.dumps(['name', 'pos_invoice', 'customer', 'vehicle', 'total_amount']),
        'limit': 50
    })
    existing = api_get(f'http://38.247.138.224:10017/api/resource/Vehicle%20POS%20Invoice?{qs}').get('data', [])
    print(f"\nCompany: {comp} currently has {len(existing)} linked POS Invoices.")
    
    needed = 10 - len(existing)
    if needed > 0:
        print(f"  -> Creating {needed} additional transactions to reach exactly 10+...")
        for i in range(needed):
            pair = verified_pairs[i % len(verified_pairs)]
            item = confirmed_items[i % len(confirmed_items)]
            amount = item['rate']
            payload = {
                "customer": pair["customer"],
                "vehicle": pair["vehicle"],
                "company": comp,
                "paid_amount": amount,
                "payment_method": "Cash",
                "items": [{
                    "item_code": item["item_code"],
                    "qty": 1.0,
                    "rate": item["rate"],
                    "discount_amount": 0.0,
                    "uom": item["uom"]
                }]
            }
            try:
                res = api_post_rpc("vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice.create_from_pos", payload)
                print(f"     [CREATED] {res.get('name')} -> POS Invoice: {res.get('pos_invoice')}")
            except Exception as e:
                print(f"     [ERROR] {e}")

# Verification of all 10 transactions per company
print("\n" + "="*95)
print("             FINAL VERIFICATION: 10 SAMPLE TRANSACTIONS PER COMPANY")
print("="*95)

grand_summary = {}
for comp in target_companies:
    qs = urllib.parse.urlencode({
        'filters': json.dumps([['company', '=', comp], ['docstatus', '=', 1], ['pos_invoice', '!=', '']]),
        'fields': json.dumps(['name', 'pos_invoice', 'customer', 'vehicle', 'total_amount', 'posting_date']),
        'limit': 20
    })
    txns = api_get(f'http://38.247.138.224:10017/api/resource/Vehicle%20POS%20Invoice?{qs}').get('data', [])
    grand_summary[comp] = txns
    print(f"\n--- COMPANY: {comp} ({len(txns)} TRANSACTIONS) ---")
    print(f"{'No.':<4} | {'Vehicle POS Inv':<18} | {'ERPNext POS Inv':<18} | {'Amount':<12} | {'Customer':<25}")
    print("-" * 95)
    for idx, t in enumerate(txns[:10], 1):
        amt = float(t.get('total_amount', 0))
        cust = (t.get('customer') or '')[:24]
        print(f"{idx:<4} | {t['name']:<18} | {t['pos_invoice']:<18} | PHP {amt:<8,.2f} | {cust:<25}")
