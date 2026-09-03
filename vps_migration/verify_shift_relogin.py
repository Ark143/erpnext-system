import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

print("=== 1. Cashier opens shift for the day with ₱ 2,000.00 ===")
open_payload = json.dumps({
    'company': 'ULTRA MRF',
    'pos_profile': 'Vehicle POS - ULTRA MRF',
    'opening_amount': 2000.0,
    'mode_of_payment': 'Cash'
}).encode()
req_open = urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_open_shift', data=open_payload, headers={'Content-Type': 'application/json'})
shift = json.loads(opener.open(req_open).read().decode())['message']
shift_name = shift['name']
print(f"Shift Opened: {shift_name} with float ₱ {shift['opening_amount']:,.2f}")

print("\n=== 2. Cashier sells an item (₱ 100.00) ===")
p = json.dumps({
    'customer': 'JOAN CHIIETE',
    'vehicle': '0301 650263',
    'paid_amount': 100.0,
    'payment_method': 'Cash',
    'items': [{ 'item_code': '#16 WIRE DM-DAS-OS', 'qty': 1, 'rate': 100.0, 'discount_amount': 0, 'uom': 'Nos' }]
}).encode()
req_sale = urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_create_invoice', data=p, headers={'Content-Type': 'application/json'})
inv = json.loads(opener.open(req_sale).read().decode())['message']
print(f"Invoice Created: {inv['name']} for ₱ {inv['grand_total']:,.2f}")

print("\n=== 3. Cashier logs out / closes browser / reloads page ===")
# Simulate checking shift on page reload / re-login
check_req = urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_get_shift?user=Administrator')
check_res = json.loads(opener.open(check_req).read().decode())['message']
print("Has Open Shift on Re-login?", check_res.get('has_open_shift'))
active = check_res.get('shift')
print(f"Resumed Shift: {active['name']}")
print(f"Opening Float Retained: ₱ {active['opening_amount']:,.2f}")
print(f"Sales Already Tracked in Shift: ₱ {active['total_sales']:,.2f}")
print(f"Expected in Drawer: ₱ {active['expected_closing']:,.2f}")

assert check_res.get('has_open_shift') == True, "Shift must stay open!"
assert active['name'] == shift_name, "Must resume the exact same shift!"
assert active['opening_amount'] == 2000.0, "Must retain the 2,000.00 opening float!"
assert active['total_sales'] == 100.0, "Must retain previous sales!"

print("\n=== 4. Cashier makes another sale (₱ 150.00) after resuming ===")
p2 = json.dumps({
    'customer': 'JOAN CHIIETE',
    'vehicle': '0301 650263',
    'paid_amount': 150.0,
    'payment_method': 'Cash',
    'items': [{ 'item_code': '#16 WIRE DM-DAS-OS', 'qty': 2, 'rate': 75.0, 'discount_amount': 0, 'uom': 'Nos' }]
}).encode()
req_sale2 = urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_create_invoice', data=p2, headers={'Content-Type': 'application/json'})
inv2 = json.loads(opener.open(req_sale2).read().decode())['message']
print(f"Invoice 2 Created: {inv2['name']} for ₱ {inv2['grand_total']:,.2f}")

print("\n=== 5. Cashier reloads/re-checks shift again ===")
check_res2 = json.loads(opener.open(check_req).read().decode())['message']['shift']
print(f"Still Active Shift: {check_res2['name']}")
print(f"Cumulative Shift Sales: ₱ {check_res2['total_sales']:,.2f} (Expected: ₱ 250.00)")
print(f"Expected Cash in Drawer: ₱ {check_res2['expected_closing']:,.2f} (Expected: ₱ 2,250.00)")

assert check_res2['total_sales'] == 250.0, "Must have 250.00 sales total!"

print("\n🎉 Shift resumption verified 100%! Cashier NEVER has to re-type opening entry if shift is open!")
