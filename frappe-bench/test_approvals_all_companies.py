import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

from vehicle_management.vehicle_management.executive_dashboard import get_approvals

companies = [r['name'] for r in frappe.db.sql('SELECT name FROM "tabCompany" WHERE name != %s', ("My Company",), as_dict=True)]

for co in companies:
    print(f"\n================ Company: {co} ================")
    res = get_approvals(co)
    for c in res:
        print(f"  {c['doctype']:22s} | Pending: {c['count']} | Value: ₱{c['total']:,.2f} | Oldest: {c['oldest_days']}d | AvgWait: {c['avg_wait_days']}d")
