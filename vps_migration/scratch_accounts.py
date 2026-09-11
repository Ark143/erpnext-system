import requests, json

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
login_res = session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=15)

def run_sql(query):
    # Call Server Script or query endpoint if available, or test via frappe.client
    pass

# Let's inspect Accounts of type Cash/Bank
accounts = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params={
    'doctype': 'Account',
    'fields': json.dumps(['name', 'account_name', 'account_type', 'root_type', 'company', 'is_group']),
    'filters': json.dumps({'account_type': ['in', ['Cash', 'Bank', 'Receivable', 'Payable']]}),
    'limit_page_length': 100
}).json().get('message', [])

print(f"Total Cash/Bank/AR/AP Accounts: {len(accounts)}")
for acc in accounts[:15]:
    print(f" - {acc['name']} | Type: {acc['account_type']} | Root: {acc['root_type']} | Co: {acc['company']}")

# Let's check unpaid/open sales invoices & purchase invoices
open_si = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params={
    'doctype': 'Sales Invoice',
    'fields': json.dumps(['name', 'company', 'customer', 'posting_date', 'due_date', 'outstanding_amount', 'grand_total', 'status']),
    'filters': json.dumps({'docstatus': 1}),
    'limit_page_length': 20
}).json().get('message', [])
print(f"\nSubmitted Sales Invoices count: {len(open_si)}")
for si in open_si[:10]:
    print(f" - SI: {si['name']} | Co: {si['company']} | Cust: {si['customer']} | Due: {si['due_date']} | Out: {si['outstanding_amount']} | Status: {si['status']}")

open_pi = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params={
    'doctype': 'Purchase Invoice',
    'fields': json.dumps(['name', 'company', 'supplier', 'posting_date', 'due_date', 'outstanding_amount', 'grand_total', 'status']),
    'filters': json.dumps({'docstatus': 1}),
    'limit_page_length': 20
}).json().get('message', [])
print(f"\nSubmitted Purchase Invoices count: {len(open_pi)}")
for pi in open_pi[:10]:
    print(f" - PI: {pi['name']} | Co: {pi['company']} | Supp: {pi['supplier']} | Due: {pi['due_date']} | Out: {pi['outstanding_amount']} | Status: {pi['status']}")
