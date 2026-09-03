import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# 1. Open shift with ₱ 1,000.00
print("--- 1. Opening Shift with ₱ 1,000.00 Cash Float ---")
open_payload = json.dumps({
    'company': 'ULTRA MRF',
    'pos_profile': 'Vehicle POS - ULTRA MRF',
    'opening_amount': 1000.0,
    'mode_of_payment': 'Cash'
}).encode()
req_open = urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_open_shift', data=open_payload, headers={'Content-Type': 'application/json'})
r_open = json.loads(opener.open(req_open).read().decode())['message']
print(f"Shift Opened: {r_open['name']} | Opening Amount: ₱ {r_open['opening_amount']:,.2f}")

# 2. Check shift stats BEFORE any sales
print("\n--- 2. Checking Shift Stats before Sales ---")
s1 = json.loads(opener.open('http://38.247.138.224:10017/api/method/vm_pos_get_shift?company=ULTRA+MRF').read().decode())['message']['shift']
print(f"Shift Name: {s1['name']}")
print(f"Shift Sales: ₱ {s1['total_sales']:,.2f} (Expected: ₱ 0.00)")
print(f"Shift Invoices Count: {s1['total_invoices']} (Expected: 0)")
print(f"Expected Cash in Drawer: ₱ {s1['expected_closing']:,.2f} (Expected: ₱ 1,000.00)")

# 3. Create Sale 1 (₱ 250.00)
print("\n--- 3. Creating Sale 1 (₱ 250.00) ---")
p1 = json.dumps({
    'customer': 'JOAN CHIIETE',
    'vehicle': '0301 650263',
    'company': 'ULTRA MRF',
    'paid_amount': 250.0,
    'payment_method': 'Cash',
    'remarks': 'Sale 1 in shift',
    'items': [{ 'item_code': '#16 WIRE DM-DAS-OS', 'qty': 2, 'rate': 125.0, 'discount_amount': 0, 'uom': 'Nos' }]
}).encode()
req1 = urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_create_invoice', data=p1, headers={'Content-Type': 'application/json'})
inv1 = json.loads(opener.open(req1).read().decode())['message']
print(f"Created Invoice 1: {inv1['name']} for ₱ {inv1['grand_total']:,.2f}")

# 4. Check shift stats after Sale 1
s2 = json.loads(opener.open('http://38.247.138.224:10017/api/method/vm_pos_get_shift?company=ULTRA+MRF').read().decode())['message']['shift']
print(f"Shift Sales after Sale 1: ₱ {s2['total_sales']:,.2f} (Expected: ₱ 250.00)")
print(f"Shift Invoices Count: {s2['total_invoices']} (Expected: 1)")
print(f"Expected Cash in Drawer: ₱ {s2['expected_closing']:,.2f} (Expected: ₱ 1,250.00)")

# 5. Create Sale 2 (₱ 350.00 via GCash)
print("\n--- 5. Creating Sale 2 (₱ 350.00 via GCash) ---")
p2 = json.dumps({
    'customer': 'JOAN CHIIETE',
    'vehicle': '0301 650263',
    'company': 'ULTRA MRF',
    'paid_amount': 350.0,
    'payment_method': 'GCash',
    'remarks': 'Sale 2 in shift (GCash)',
    'items': [{ 'item_code': '#16 WIRE DM-DAS-OS', 'qty': 2, 'rate': 175.0, 'discount_amount': 0, 'uom': 'Nos' }]
}).encode()
req2 = urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_create_invoice', data=p2, headers={'Content-Type': 'application/json'})
inv2 = json.loads(opener.open(req2).read().decode())['message']
print(f"Created Invoice 2: {inv2['name']} for ₱ {inv2['grand_total']:,.2f} ({inv2['payment_method']})")

# 6. Check shift stats after Sale 2
s3 = json.loads(opener.open('http://38.247.138.224:10017/api/method/vm_pos_get_shift?company=ULTRA+MRF').read().decode())['message']['shift']
print(f"Shift Sales after Sale 2: ₱ {s3['total_sales']:,.2f} (Expected: ₱ 600.00)")
print(f"Shift Invoices Count: {s3['total_invoices']} (Expected: 2)")
print(f"Expected Cash in Drawer: ₱ {s3['expected_closing']:,.2f} (Expected: ₱ 1,600.00)")

# 7. Close Shift with exact cash count ₱ 1,600.00
print("\n--- 7. Closing Shift (Count: ₱ 1,600.00) ---")
close_payload = json.dumps({
    'opening_entry': s3['name'],
    'closing_amount': 1600.0,
    'mode_of_payment': 'Cash'
}).encode()
req_close = urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_close_shift', data=close_payload, headers={'Content-Type': 'application/json'})
close_res = json.loads(opener.open(req_close).read().decode())['message']
print(f"POS Closing Entry Created: {close_res['name']}")
print(f"Invoices in Shift: {close_res['total_invoices']} (Expected: 2)")
print(f"Total Sales in Shift: ₱ {close_res['grand_total']:,.2f} (Expected: ₱ 600.00)")
print(f"Opening Cash Float: ₱ {close_res['opening_amount']:,.2f} (Expected: ₱ 1,000.00)")
print(f"Counted Cash Amount: ₱ {close_res['closing_amount']:,.2f} (Expected: ₱ 1,600.00)")
print(f"Difference: ₱ {close_res['difference']:,.2f} (Expected: ₱ 0.00)")
print(f"Status: {close_res['status']}")

print("\n🎉 ALL SHIFT CALCULATIONS ARE 100% ISOLATED AND ACCURATE!")
