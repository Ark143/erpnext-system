import requests, json

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
login_res = session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=15)
print("Login:", login_res.status_code)

def get_list(doctype, fields, filters=None, limit_page_length=20):
    params = {
        'doctype': doctype,
        'fields': json.dumps(fields),
        'limit_page_length': limit_page_length
    }
    if filters:
        params['filters'] = json.dumps(filters)
    r = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params=params)
    return r.json().get('message', [])

companies = get_list('Company', ['name', 'abbr', 'default_currency'])
print(f"Total Companies ({len(companies)}):")
for c in companies:
    print(f" - {c['name']} ({c.get('abbr')})")

sales_invoices = get_list('Sales Invoice', ['name', 'company', 'customer', 'posting_date', 'due_date', 'payment_terms_template', 'grand_total', 'outstanding_amount', 'status'], limit_page_length=5)
print("\nSample Sales Invoices:")
for si in sales_invoices:
    print(si)

purchase_invoices = get_list('Purchase Invoice', ['name', 'company', 'supplier', 'posting_date', 'due_date', 'payment_terms_template', 'grand_total', 'outstanding_amount', 'status'], limit_page_length=5)
print("\nSample Purchase Invoices:")
for pi in purchase_invoices:
    print(pi)

# Check payment terms / schedule
payment_terms = get_list('Payment Term', ['name', 'payment_term_name', 'credit_days', 'credit_months'], limit_page_length=10)
print("\nPayment Terms:", payment_terms)

payment_templates = get_list('Payment Terms Template', ['name', 'template_name'], limit_page_length=10)
print("\nPayment Terms Templates:", payment_templates)
