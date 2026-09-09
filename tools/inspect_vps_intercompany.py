import requests
import json
import sys

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f'{BASE_URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

print("=== Companies ===")
comps = session.get(f'{BASE_URL}/api/resource/Company?fields=["name","abbr","default_currency","default_receivable_account","default_payable_account","default_bank_account","default_cash_account"]').json().get('data', [])
for c in comps:
    print(c['name'], f"({c.get('abbr')})")

print("\n=== Leaf Warehouses ===")
whs = session.get(f'{BASE_URL}/api/resource/Warehouse?fields=["name","company","is_group"]&limit_page_length=100').json().get('data', [])
for w in whs:
    if not w.get('is_group'):
        print(f"  {w['name']} -> {w['company']}")

print("\n=== Stocked Bins ===")
bins = session.get(f'{BASE_URL}/api/resource/Bin?filters=[["actual_qty",">",0]]&fields=["item_code","warehouse","actual_qty"]&limit_page_length=20').json().get('data', [])
for b in bins:
    print(f"  Item: {b['item_code']} | WH: {b['warehouse']} | Qty: {b['actual_qty']}")

print("\n=== Intercompany Customers ===")
custs = session.get(f'{BASE_URL}/api/resource/Customer?filters=[["is_internal_customer","=",1]]&fields=["name","customer_name","represents_company"]&limit_page_length=50').json().get('data', [])
for cu in custs:
    print(f"  Customer: {cu['name']} -> Represents: {cu.get('represents_company')}")

print("\n=== Intercompany Suppliers ===")
supps = session.get(f'{BASE_URL}/api/resource/Supplier?filters=[["is_internal_supplier","=",1]]&fields=["name","supplier_name","represents_company"]&limit_page_length=50').json().get('data', [])
for su in supps:
    print(f"  Supplier: {su['name']} -> Represents: {su.get('represents_company')}")
