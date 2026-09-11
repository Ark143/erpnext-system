import requests, json
from datetime import datetime

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=15)

# Let's test GL entries on VPS
gl_res = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params={
    'doctype': 'GL Entry',
    'fields': json.dumps(['name', 'posting_date', 'company', 'account', 'debit', 'credit', 'voucher_type', 'voucher_no', 'against']),
    'limit_page_length': 20
})
print("GL entries found:", len(gl_res.json().get('message', [])))

# Let's test Sales Invoice on VPS
si_res = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params={
    'doctype': 'Sales Invoice',
    'fields': json.dumps(['name', 'customer', 'customer_name', 'company', 'posting_date', 'due_date', 'grand_total', 'outstanding_amount', 'status']),
    'limit_page_length': 20
})
print("Sales Invoices found:", len(si_res.json().get('message', [])))
for s in si_res.json().get('message', [])[:5]:
    print(" - SI:", s)

# Let's test Purchase Invoice on VPS
pi_res = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params={
    'doctype': 'Purchase Invoice',
    'fields': json.dumps(['name', 'supplier', 'supplier_name', 'company', 'posting_date', 'due_date', 'grand_total', 'outstanding_amount', 'status']),
    'limit_page_length': 20
})
print("Purchase Invoices found:", len(pi_res.json().get('message', [])))
for p in pi_res.json().get('message', [])[:5]:
    print(" - PI:", p)
