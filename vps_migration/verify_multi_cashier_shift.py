import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

print("=== Multi-Cashier Isolation Test in Same Company (ULTRA MRF) ===")

# Cashier 1: Administrator
c1 = 'Administrator'
r1 = json.loads(opener.open(f'http://38.247.138.224:10017/api/method/vm_pos_get_shift?user={c1}').read().decode())['message']['shift']
print(f"\n[Cashier 1: {c1}]")
print(f"  Shift: {r1['name']}")
print(f"  Opening Float: ₱ {r1['opening_amount']:,.2f}")
print(f"  Today Sales: ₱ {r1['total_sales']:,.2f}")
print(f"  Invoices Today: {r1['total_invoices']}")
print(f"  Expected Drawer: ₱ {r1['expected_closing']:,.2f}")

# Cashier 2: cashier.test@example.com
c2 = 'cashier.test@example.com'

# Open shift for Cashier 2 if needed
open_payload = json.dumps({
    'user': c2,
    'company': 'ULTRA MRF',
    'pos_profile': 'Vehicle POS - ULTRA MRF',
    'opening_amount': 500.0,
    'mode_of_payment': 'Cash'
}).encode()
req_open = urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_open_shift', data=open_payload, headers={'Content-Type': 'application/json'})
opener.open(req_open)

# Cashier 2 processes 1 invoice for ₱ 300.00
sale_payload = json.dumps({
    'user': c2,
    'customer': 'JOAN CHIIETE',
    'vehicle': '0301 650263',
    'company': 'ULTRA MRF',
    'paid_amount': 300.0,
    'payment_method': 'Cash',
    'remarks': 'Sale by Cashier 2',
    'items': [{ 'item_code': '#16 WIRE DM-DAS-OS', 'qty': 2, 'rate': 150.0, 'discount_amount': 0, 'uom': 'Nos' }]
}).encode()
req_sale = urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_create_invoice', data=sale_payload, headers={'Content-Type': 'application/json'})
inv_c2 = json.loads(opener.open(req_sale).read().decode())['message']
print(f"\n[Cashier 2: {c2}] Processed invoice: {inv_c2['name']} for ₱ {inv_c2['grand_total']:,.2f}")

# Query Cashier 2 shift
r2 = json.loads(opener.open(f'http://38.247.138.224:10017/api/method/vm_pos_get_shift?user={c2}').read().decode())['message']['shift']
print(f"\n[Cashier 2: {c2}] Summary:")
print(f"  Shift: {r2['name']}")
print(f"  Opening Float: ₱ {r2['opening_amount']:,.2f}")
print(f"  Today Sales: ₱ {r2['total_sales']:,.2f} (Expected: ₱ 300.00)")
print(f"  Invoices Today: {r2['total_invoices']} (Expected: 1)")
print(f"  Expected Drawer: ₱ {r2['expected_closing']:,.2f} (Expected: ₱ 800.00)")

# Re-query Cashier 1 shift to confirm ZERO contamination
r1_again = json.loads(opener.open(f'http://38.247.138.224:10017/api/method/vm_pos_get_shift?user={c1}').read().decode())['message']['shift']
print(f"\n[Cashier 1: {c1}] Re-check Summary:")
print(f"  Today Sales: ₱ {r1_again['total_sales']:,.2f} (Expected: ₱ 22,512.50)")
print(f"  Invoices Today: {r1_again['total_invoices']} (Expected: 6)")

assert r2['total_sales'] == 300.0, "Cashier 2 must only have their 300.00 sales!"
assert r2['total_invoices'] == 1, "Cashier 2 must only have 1 invoice!"
assert r1_again['total_sales'] == 22512.5, "Cashier 1 must remain 22,512.50!"
assert r1_again['total_invoices'] == 6, "Cashier 1 must remain 6 invoices!"

print("\n🎉 MULTI-CASHIER ISOLATION VERIFIED 100%! Each cashier's closing entry is completely independent!")
