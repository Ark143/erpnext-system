import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

from vehicle_management.vehicle_management.executive_dashboard import get_approvals

companies = frappe.get_list("Company", filters={"name": ["!=", "My Company"]}, pluck="name")

for co in companies:
    print(f"\n🏢 === Company: {co} ===")
    cards = get_approvals(co)
    pending_cards = [c for c in cards if c['count'] > 0]
    for c in pending_cards:
        print(f"  • {c['doctype']:22s} | Pending: {c['count']} | Value: ₱{c['total']:,.2f} | Oldest: {c['oldest_days']}d | AvgWait: {c['avg_wait_days']}d")
