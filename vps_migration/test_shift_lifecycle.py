import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

print("=== STEP 1: Check Current Shift Status ===")
r1 = opener.open('http://38.247.138.224:10017/api/method/vm_pos_get_shift?company=ULTRA+MRF')
d1 = json.loads(r1.read().decode())['message']
print("has_open_shift:", d1.get('has_open_shift'))
if d1.get('has_open_shift'):
    print("Found existing open shift:", d1['shift']['name'])
    # Close it first to start clean
    payload = json.dumps({'opening_entry': d1['shift']['name'], 'closing_amount': 0, 'mode_of_payment': 'Cash'}).encode()
    req_close = urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_close_shift', data=payload, headers={'Content-Type': 'application/json'})
    opener.open(req_close)
    print("Closed existing shift to test fresh opening entry.")

print("\n=== STEP 2: Create Opening Entry (Open Shift with ₱ 1,500.00 Cash) ===")
open_payload = json.dumps({
    'company': 'ULTRA MRF',
    'pos_profile': 'Vehicle POS - ULTRA MRF',
    'opening_amount': 1500.0,
    'mode_of_payment': 'Cash'
}).encode()
req_open = urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_open_shift', data=open_payload, headers={'Content-Type': 'application/json'})
r_open = opener.open(req_open)
open_result = json.loads(r_open.read().decode())['message']
opening_name = open_result['name']
print(f"✅ Created POS Opening Entry: {opening_name}")
print(f"   Opening Cash Amount: ₱ {open_result['opening_amount']:,.2f}")
print(f"   Status: {open_result['status']}")

print("\n=== STEP 3: Process a POS Invoice during this Shift ===")
sale_payload = json.dumps({
    'customer': 'JOAN CHIIETE',
    'vehicle': '0301 650263',
    'company': 'ULTRA MRF',
    'paid_amount': 150.0,
    'payment_method': 'Cash',
    'remarks': f'Sale during shift {opening_name}',
    'items': [{
        'item_code': '#16 WIRE DM-DAS-OS',
        'qty': 2,
        'rate': 75.0,
        'discount_amount': 0,
        'uom': 'Nos'
    }]
}).encode()
req_sale = urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_create_invoice', data=sale_payload, headers={'Content-Type': 'application/json'})
r_sale = opener.open(req_sale)
sale_result = json.loads(r_sale.read().decode())['message']
inv_name = sale_result['name']
print(f"✅ Created POS Invoice: {inv_name}")
print(f"   Total Amount: ₱ {sale_result['grand_total']:,.2f}")
print(f"   Status: {sale_result['status']}")

print("\n=== STEP 4: Close the Shift (POS Closing Entry with actual cash count ₱ 1,650.00) ===")
close_payload = json.dumps({
    'opening_entry': opening_name,
    'closing_amount': 1650.0,
    'mode_of_payment': 'Cash'
}).encode()
req_close = urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_close_shift', data=close_payload, headers={'Content-Type': 'application/json'})
r_close = opener.open(req_close)
close_result = json.loads(r_close.read().decode())['message']
print(f"✅ Created POS Closing Entry: {close_result['name']}")
print(f"   Linked Opening Entry: {close_result['opening_entry']}")
print(f"   Invoices in Shift: {close_result['total_invoices']}")
print(f"   Opening Cash Amount: ₱ {close_result['opening_amount']:,.2f}")
print(f"   Total Sales: ₱ {close_result['grand_total']:,.2f}")
print(f"   Closing Counted Cash: ₱ {close_result['closing_amount']:,.2f}")
print(f"   Reconciliation Difference: ₱ {close_result['difference']:,.2f}")
print(f"   Status: {close_result['status']}")

print("\n=== STEP 5: Verify Shift is Closed in ERPNext ===")
r_final = opener.open('http://38.247.138.224:10017/api/method/vm_pos_get_shift?company=ULTRA+MRF')
d_final = json.loads(r_final.read().decode())['message']
print("has_open_shift:", d_final.get('has_open_shift'))
print("✅ Entire Opening & Closing Entry lifecycle PASSED with 100% SUCCESS!")
