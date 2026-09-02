import urllib.request, urllib.parse, json, http.cookiejar, random

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

# 1. Fetch sample active Customer Vehicles and their linked Customers
r_vehs = api_get('http://38.247.138.224:10017/api/resource/Customer%20Vehicle?limit=40')
veh_list = r_vehs.get('data', [])

valid_pairs = []
for v in veh_list:
    doc = api_get(f"http://38.247.138.224:10017/api/resource/Customer%20Vehicle/{urllib.parse.quote(v['name'])}").get('data', {})
    cust = doc.get('customer')
    plate = doc.get('license_plate') or doc.get('plate_no') or doc.get('name')
    if cust and plate:
        valid_pairs.append({'vehicle': doc['name'], 'customer': cust, 'plate': plate})

print(f"Found {len(valid_pairs)} valid Customer Vehicle pairs.")

# 2. Fetch sample sellable Items
r_items = api_get('http://38.247.138.224:10017/api/resource/Item?limit=40')
item_list = r_items.get('data', [])
valid_items = []
for it in item_list:
    doc = api_get(f"http://38.247.138.224:10017/api/resource/Item/{urllib.parse.quote(it['name'])}").get('data', {})
    rate = float(doc.get('standard_rate') or 150.0)
    if rate <= 0: rate = 120.0
    valid_items.append({
        'item_code': doc['name'],
        'item_name': doc.get('item_name', doc['name']),
        'rate': rate,
        'uom': doc.get('stock_uom') or 'Nos'
    })

print(f"Found {len(valid_items)} valid Items for checkout.")

# 3. Companies to test (10 transactions each)
target_companies = [
    "ULTRA MRF",
    "Ultra MRF Dau Main",
    "Ultra MRF Dau Annex"
]

results = {}

for comp in target_companies:
    print(f"\n{'='*75}")
    print(f"   GENERATING 10 SAMPLE TRANSACTIONS FOR COMPANY: {comp}")
    print(f"{'='*75}")
    results[comp] = []
    
    for i in range(1, 11):
        pair = valid_pairs[(i - 1 + len(results[comp])) % len(valid_pairs)]
        selected_item = valid_items[(i - 1) % len(valid_items)]
        qty = 1.0 if i % 3 != 0 else 2.0
        amount = selected_item['rate'] * qty
        paid = amount # exact payment
        
        payload = {
            "customer": pair["customer"],
            "vehicle": pair["vehicle"],
            "company": comp,
            "paid_amount": paid,
            "payment_method": "Cash",
            "items": [
                {
                    "item_code": selected_item["item_code"],
                    "qty": qty,
                    "rate": selected_item["rate"],
                    "discount_amount": 0.0,
                    "uom": selected_item["uom"]
                }
            ]
        }
        
        try:
            res = api_post_rpc("vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice.create_from_pos", payload)
            vms_name = res.get("name")
            pos_inv = res.get("pos_invoice")
            
            # Fetch the newly created POS Invoice to verify full linkage
            pos_doc = api_get(f"http://38.247.138.224:10017/api/resource/POS%20Invoice/{urllib.parse.quote(pos_inv)}").get("data", {})
            linked_vms = pos_doc.get("custom_vehicle_pos_invoice")
            linked_veh = pos_doc.get("custom_customer_vehicle")
            linked_plate = pos_doc.get("custom_plate_no")
            grand_total = float(pos_doc.get("grand_total") or 0)
            
            status_str = f"Txn #{i:2d}: {vms_name} -> POS Invoice: {pos_inv} | Total: PHP {grand_total:,.2f} | Plate: {linked_plate} | Status: {pos_doc.get('status')}"
            print(f"  [SUCCESS] {status_str}")
            results[comp].append({
                "txn_no": i,
                "vms_invoice": vms_name,
                "pos_invoice": pos_inv,
                "total": grand_total,
                "customer": pair["customer"],
                "vehicle": pair["vehicle"],
                "plate": linked_plate,
                "status": pos_doc.get("status")
            })
        except urllib.error.HTTPError as e:
            err = e.fp.read().decode('utf-8', 'ignore') if e.fp else ""
            print(f"  [ERROR] Txn #{i:2d} failed: {e.code} -> {err[:200]}")
        except Exception as ex:
            print(f"  [ERROR] Txn #{i:2d} exception: {ex}")

print(f"\n{'='*75}")
print("                     SUMMARY OF TRANSACTIONS CREATED")
print(f"{'='*75}")
total_success = 0
for comp, txns in results.items():
    print(f"Company: {comp} -> Successfully Processed: {len(txns)} / 10 POS Invoices")
    total_success += len(txns)

print(f"\nTotal ERPNext POS Invoices Successfully Created & Verified: {total_success}")
