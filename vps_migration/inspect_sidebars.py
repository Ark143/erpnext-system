import requests, json

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=15)

# Check Workspace Sidebars
sb_list = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params={
    'doctype': 'Workspace Sidebar',
    'fields': json.dumps(['name', 'title', 'module']),
    'limit_page_length': 50
}).json().get('message', [])

print("Workspace Sidebars:")
for sb in sb_list:
    print(f" - {sb['name']} (Module: {sb.get('module')})")

# Let's inspect Financial Reports or Accounts sidebar
if sb_list:
    sample_sb = session.get(f"{BASE_URL}/api/resource/Workspace%20Sidebar/{sb_list[0]['name']}").json().get('data', {})
    print(f"\nSample Sidebar '{sb_list[0]['name']}' items count:", len(sample_sb.get('items', [])))
    for it in sample_sb.get('items', [])[:5]:
        print("   * Item:", it.get('label') or it.get('title'), "| Type:", it.get('type') or it.get('link_type'), "| Target:", it.get('link_to') or it.get('url'))
