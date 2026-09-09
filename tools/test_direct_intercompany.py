import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
login_res = session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'})
login_res.raise_for_status()

SELLER_COMPANY = 'Ultra MRF Warehouse Dau'
SELLER_ABBR = 'UMDW'
SELLER_WH = 'Stores - UMDW'
SELLER_CUSTOMER = 'Ultra MRF Dau Main'

BUYER_COMPANY = 'Ultra MRF Dau Main'
BUYER_ABBR = 'UMDM'
BUYER_WH = 'Stores - UMDM'
BUYER_SUPPLIER = 'ULTRA MRF WAREHOUSE DAU'

ITEM_CODE = 'STRL-CAR PROTECT KIT (CAR CLEAN SET)'
QTY = 2.0
RATE = 1500.00
TODAY = '2026-09-08'

def post_and_submit(doctype, payload):
    r = session.post(f"{BASE_URL}/api/resource/{requests.utils.quote(doctype)}", json=payload)
    if r.status_code != 200:
        raise Exception(f"Failed to create {doctype}: {r.status_code} - {r.text}")
    doc = r.json().get('data', {})
    doc_name = doc['name']
    
    doc['docstatus'] = 1
    r_sub = session.put(f"{BASE_URL}/api/resource/{requests.utils.quote(doctype)}/{requests.utils.quote(doc_name)}", json=doc)
    if r_sub.status_code != 200:
        raise Exception(f"Failed to submit {doctype} {doc_name}: {r_sub.status_code} - {r_sub.text}")
    return r_sub.json().get('data', {})

print("\n--- STEP 1: Purchase Order (Buyer: Branch) ---")
po = post_and_submit('Purchase Order', {
    'doctype': 'Purchase Order',
    'company': BUYER_COMPANY,
    'supplier': BUYER_SUPPLIER,
    'transaction_date': TODAY,
    'schedule_date': TODAY,
    'set_posting_time': 1,
    'currency': 'PHP',
    'is_internal_supplier': 1,
    'represents_company': SELLER_COMPANY,
    'items': [{
        'item_code': ITEM_CODE,
        'qty': QTY,
        'rate': RATE,
        'warehouse': BUYER_WH,
        'schedule_date': TODAY
    }]
})
print("PO Submitted:", po['name'])

print("\n--- STEP 2: Delivery Note (Seller / Shipper: Main Warehouse) ---")
dn = post_and_submit('Delivery Note', {
    'doctype': 'Delivery Note',
    'company': SELLER_COMPANY,
    'customer': SELLER_CUSTOMER,
    'posting_date': TODAY,
    'set_posting_time': 1,
    'currency': 'PHP',
    'is_internal_customer': 1,
    'represents_company': BUYER_COMPANY,
    'intercompany_order_reference': po['name'],
    'items': [{
        'item_code': ITEM_CODE,
        'qty': QTY,
        'rate': RATE,
        'warehouse': SELLER_WH
    }]
})
print("DN Submitted:", dn['name'])

print("\n--- STEP 3: Purchase Receipt (Buyer / Receiver: Branch) ---")
pr = post_and_submit('Purchase Receipt', {
    'doctype': 'Purchase Receipt',
    'company': BUYER_COMPANY,
    'supplier': BUYER_SUPPLIER,
    'posting_date': TODAY,
    'set_posting_time': 1,
    'currency': 'PHP',
    'is_internal_supplier': 1,
    'represents_company': SELLER_COMPANY,
    'intercompany_reference': dn['name'],
    'items': [{
        'item_code': ITEM_CODE,
        'qty': QTY,
        'rate': RATE,
        'warehouse': BUYER_WH,
        'purchase_order': po['name'],
        'purchase_order_item': po['items'][0]['name']
    }]
})
print("PR Submitted:", pr['name'])

print("\n--- STEP 4: Sales Invoice (Seller / Billing: Main Warehouse) ---")
si = post_and_submit('Sales Invoice', {
    'doctype': 'Sales Invoice',
    'company': SELLER_COMPANY,
    'customer': SELLER_CUSTOMER,
    'posting_date': TODAY,
    'due_date': TODAY,
    'set_posting_time': 1,
    'currency': 'PHP',
    'is_internal_customer': 1,
    'represents_company': BUYER_COMPANY,
    'update_stock': 0,
    'debit_to': f'Debtors - {SELLER_ABBR}',
    'items': [{
        'item_code': ITEM_CODE,
        'qty': QTY,
        'rate': RATE,
        'income_account': f'Sales - {SELLER_ABBR}',
        'cost_center': f'Main - {SELLER_ABBR}',
        'delivery_note': dn['name'],
        'dn_detail': dn['items'][0]['name']
    }]
})
print("SI Submitted:", si['name'])

print("\n--- STEP 5: Purchase Invoice (Buyer / AP: Branch) ---")
pi = post_and_submit('Purchase Invoice', {
    'doctype': 'Purchase Invoice',
    'company': BUYER_COMPANY,
    'supplier': BUYER_SUPPLIER,
    'posting_date': TODAY,
    'due_date': TODAY,
    'set_posting_time': 1,
    'currency': 'PHP',
    'is_internal_supplier': 1,
    'represents_company': SELLER_COMPANY,
    'intercompany_invoice_reference': si['name'],
    'credit_to': f'Creditors - {BUYER_ABBR}',
    'items': [{
        'item_code': ITEM_CODE,
        'qty': QTY,
        'rate': RATE,
        'expense_account': f'Stock Received But Not Billed - {BUYER_ABBR}',
        'cost_center': f'Main - {BUYER_ABBR}',
        'purchase_order': po['name'],
        'po_detail': po['items'][0]['name'],
        'purchase_receipt': pr['name'],
        'pr_detail': pr['items'][0]['name']
    }]
})
print("PI Submitted:", pi['name'])

print("\n--- STEP 6: Payment Entry (Branch Outgoing Pay) ---")
pe_pay = post_and_submit('Payment Entry', {
    'doctype': 'Payment Entry',
    'payment_type': 'Pay',
    'company': BUYER_COMPANY,
    'party_type': 'Supplier',
    'party': BUYER_SUPPLIER,
    'posting_date': TODAY,
    'set_posting_time': 1,
    'mode_of_payment': 'Cash',
    'paid_from': f'Cash - {BUYER_ABBR}',
    'paid_to': f'Creditors - {BUYER_ABBR}',
    'paid_amount': QTY * RATE,
    'received_amount': QTY * RATE,
    'target_exchange_rate': 1.0,
    'references': [{
        'reference_doctype': 'Purchase Invoice',
        'reference_name': pi['name'],
        'total_amount': QTY * RATE,
        'outstanding_amount': QTY * RATE,
        'allocated_amount': QTY * RATE
    }]
})
print("PE Pay Submitted:", pe_pay['name'])

print("\n--- STEP 7: Payment Entry (Main Warehouse Incoming Receive) ---")
pe_recv = post_and_submit('Payment Entry', {
    'doctype': 'Payment Entry',
    'payment_type': 'Receive',
    'company': SELLER_COMPANY,
    'party_type': 'Customer',
    'party': SELLER_CUSTOMER,
    'posting_date': TODAY,
    'set_posting_time': 1,
    'mode_of_payment': 'Cash',
    'paid_from': f'Debtors - {SELLER_ABBR}',
    'paid_to': f'Cash - {SELLER_ABBR}',
    'paid_amount': QTY * RATE,
    'received_amount': QTY * RATE,
    'target_exchange_rate': 1.0,
    'references': [{
        'reference_doctype': 'Sales Invoice',
        'reference_name': si['name'],
        'total_amount': QTY * RATE,
        'outstanding_amount': QTY * RATE,
        'allocated_amount': QTY * RATE
    }]
})
print("PE Receive Submitted:", pe_recv['name'])

print("\n" + "="*80)
print(">>> ALL INTERCOMPANY TRANSACTIONS SUBMITTED AND FULLY SETTLED! <<<")
print("="*80)
