import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'})

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
TOTAL = QTY * RATE
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

print("Testing Sales Invoice with update_stock=1...")
try:
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
        'update_stock': 1,
        'debit_to': f'Debtors - {SELLER_ABBR}',
        'items': [{
            'item_code': ITEM_CODE,
            'qty': QTY,
            'rate': RATE,
            'warehouse': SELLER_WH,
            'income_account': f'Sales - {SELLER_ABBR}',
            'expense_account': f'Cost of Goods Sold - {SELLER_ABBR}',
            'cost_center': f'Main - {SELLER_ABBR}'
        }]
    })
    print("SI with stock update SUCCESS:", si['name'])
except Exception as e:
    print("SI with stock update Err:", e)

print("\nTesting Purchase Invoice with update_stock=1...")
try:
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
        'update_stock': 1,
        'credit_to': f'Creditors - {BUYER_ABBR}',
        'items': [{
            'item_code': ITEM_CODE,
            'qty': QTY,
            'rate': RATE,
            'set_warehouse': BUYER_WH,
            'warehouse': BUYER_WH,
            'expense_account': f'Cost of Goods Sold - {BUYER_ABBR}',
            'cost_center': f'Main - {BUYER_ABBR}'
        }]
    })
    print("PI with stock update SUCCESS:", pi['name'])
except Exception as e:
    print("PI with stock update Err:", e)
