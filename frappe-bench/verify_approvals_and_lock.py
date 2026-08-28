import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
from frappe.handler import run_server_script

frappe.init(site='erp.localhost')
frappe.connect()

print("=== 1. Testing Approvals Endpoint ===")
frappe.form_dict = frappe._dict({'view': 'approvals', 'company': 'Ultra MRF Dau Main'})
approvals = run_server_script('Executive Dashboard API')
print(f"Total Approval Doctypes Tracked: {len(approvals)}")
for card in approvals:
    print(f"  - {card['doctype']:22s} | Pending: {card['count']} | Value: ₱{card['total']:,.2f} | Oldest: {card['oldest_days']}d")

print("\n=== 2. Verifying Company Lock Configurations in Web Pages ===")
pages = frappe.db.sql('SELECT name, route, title, LENGTH(main_section_html) as len FROM "tabWeb Page" WHERE route LIKE "executive%" ORDER BY route', as_dict=True)
for p in pages:
    print(f"  [{p['route']:38s}] {p['title']}")
