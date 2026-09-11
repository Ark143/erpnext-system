import requests, json

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=15)

# Test query GL entries and Accounts
print("Testing accounts...")
accs = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params={
    'doctype': 'Account',
    'fields': json.dumps(['name', 'account_name', 'account_type', 'root_type', 'company']),
    'filters': json.dumps({'is_group': 0}),
    'limit_page_length': 500
}).json().get('message', [])

cash_accs = [a for a in accs if a.get('account_type') in ('Cash', 'Bank') or 'cash' in a.get('account_name', '').lower() or 'bank' in a.get('account_name', '').lower()]
print(f"Total Cash/Bank leaf accounts: {len(cash_accs)}")

# Test Sales Invoices
sis = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params={
    'doctype': 'Sales Invoice',
    'fields': json.dumps(['name', 'customer', 'customer_name', 'company', 'posting_date', 'due_date', 'grand_total', 'outstanding_amount', 'status']),
    'limit_page_length': 500
}).json().get('message', [])
print(f"Total Sales Invoices: {len(sis)}")

# Test Purchase Invoices
pis = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params={
    'doctype': 'Purchase Invoice',
    'fields': json.dumps(['name', 'supplier', 'supplier_name', 'company', 'posting_date', 'due_date', 'grand_total', 'outstanding_amount', 'status']),
    'limit_page_length': 500
}).json().get('message', [])
print(f"Total Purchase Invoices: {len(pis)}")
