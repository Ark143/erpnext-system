import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'})

SELLER_COMPANY = 'Ultra MRF Warehouse Dau'
SELLER_WH = 'Stores - UMDW'
BUYER_COMPANY = 'Ultra MRF Dau Main'
BUYER_WH = 'Stores - UMDM'
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

print("\n--- TEST: Stock Movement (Material Issue from Warehouse) ---")
try:
    se_issue = post_and_submit('Stock Entry', {
        'doctype': 'Stock Entry',
        'stock_entry_type': 'Material Issue',
        'company': SELLER_COMPANY,
        'posting_date': TODAY,
        'set_posting_time': 1,
        'items': [{
            'item_code': ITEM_CODE,
            'qty': QTY,
            's_warehouse': SELLER_WH,
            'basic_rate': RATE
        }]
    })
    print("Stock Issue Submitted:", se_issue['name'])
except Exception as e:
    print("Stock Issue Err:", e)

print("\n--- TEST: Stock Movement (Material Receipt at Branch) ---")
try:
    se_rcpt = post_and_submit('Stock Entry', {
        'doctype': 'Stock Entry',
        'stock_entry_type': 'Material Receipt',
        'company': BUYER_COMPANY,
        'posting_date': TODAY,
        'set_posting_time': 1,
        'items': [{
            'item_code': ITEM_CODE,
            'qty': QTY,
            't_warehouse': BUYER_WH,
            'basic_rate': RATE
        }]
    })
    print("Stock Receipt Submitted:", se_rcpt['name'])
except Exception as e:
    print("Stock Receipt Err:", e)
