import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def api_get(url):
    req = urllib.request.Request(url, headers=H)
    return json.loads(op.open(req).read().decode())

def api_put(doctype, name, doc):
    req = urllib.request.Request(
        f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(doctype)}/{urllib.parse.quote(name)}',
        data=urllib.parse.urlencode({'data': json.dumps(doc)}).encode(),
        headers=H
    )
    req.get_method = lambda: 'PUT'
    return json.loads(op.open(req).read().decode()).get('data', {})

# Fetch all Vehicle POS Invoices
vpis = api_get('http://38.247.138.224:10017/api/resource/Vehicle%20POS%20Invoice?limit=100').get('data', [])

print(f"Linking {len(vpis)} Vehicle POS Invoices to ERPNext POS Invoices...")
for v in vpis:
    doc = api_get(f"http://38.247.138.224:10017/api/resource/Vehicle%20POS%20Invoice/{urllib.parse.quote(v['name'])}").get('data', {})
    pos_inv = doc.get('pos_invoice')
    veh = doc.get('vehicle')
    if pos_inv:
        plate = ""
        if veh:
            try:
                veh_doc = api_get(f"http://38.247.138.224:10017/api/resource/Customer%20Vehicle/{urllib.parse.quote(veh)}").get('data', {})
                plate = veh_doc.get('license_plate') or veh_doc.get('plate_no') or ""
            except Exception:
                pass
        
        try:
            res = api_put('POS Invoice', pos_inv, {
                'custom_vehicle_pos_invoice': doc['name'],
                'custom_customer_vehicle': veh or "",
                'custom_plate_no': plate
            })
            print(f"[OK] Linked {pos_inv} -> Vehicle POS Invoice: {doc['name']} | Vehicle: {veh} | Plate: {plate}")
        except urllib.error.HTTPError as e:
            print(f"Error linking {pos_inv}: {e.code}")

print("\n--- Verification: All ERPNext POS Invoices with Vehicle Linkage ---")
pis = api_get('http://38.247.138.224:10017/api/resource/POS%20Invoice?limit=50').get('data', [])
for p in pis:
    p_doc = api_get(f"http://38.247.138.224:10017/api/resource/POS%20Invoice/{urllib.parse.quote(p['name'])}").get('data', {})
    print(f"[{p_doc['name']}] Customer: {p_doc.get('customer')} | Total: PHP {p_doc.get('grand_total')} | VMS: {p_doc.get('custom_vehicle_pos_invoice')} | Vehicle: {p_doc.get('custom_customer_vehicle')} | Plate: {p_doc.get('custom_plate_no')}")
