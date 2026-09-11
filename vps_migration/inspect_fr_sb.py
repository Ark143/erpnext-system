import requests, json

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=15)

# Inspect Financial Reports Sidebar
fr_sb = session.get(f"{BASE_URL}/api/resource/Workspace%20Sidebar/Financial%20Reports").json().get('data', {})
print("Financial Reports Sidebar items:")
for it in fr_sb.get('items', []):
    print(f" - {it.get('label') or it.get('title')} | Type: {it.get('type') or it.get('link_type')} | Target: {it.get('link_to') or it.get('url')}")

# Inspect Invoicing Sidebar
inv_sb = session.get(f"{BASE_URL}/api/resource/Workspace%20Sidebar/Invoicing").json().get('data', {})
print("\nInvoicing Sidebar items:")
for it in inv_sb.get('items', []):
    print(f" - {it.get('label') or it.get('title')} | Type: {it.get('type') or it.get('link_type')} | Target: {it.get('link_to') or it.get('url')}")

# Inspect Page doctypes
pages = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params={
    'doctype': 'Page',
    'fields': json.dumps(['name', 'title', 'module']),
    'limit_page_length': 50
}).json().get('message', [])
print(f"\nTotal Pages in Desk ({len(pages)}):")
for p in pages:
    print(f" - Page: {p['name']} (Title: {p.get('title')}, Module: {p.get('module')})")
