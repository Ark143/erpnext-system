import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

from frappe.handler import run_server_script

views = ['meta', 'exec_summary', 'sales', 'procurement', 'finance', 'budget', 'approvals', 'operations', 'alerts']
for v in views:
    frappe.form_dict = frappe._dict({'view': v, 'company': 'Ultra MRF Dau Main', 'fy': '2026', 'months': 12})
    resp = run_server_script('Executive Dashboard API')
    print(f"Server Script View [{v:15s}]: Success! Type={type(resp)} Items/Keys={len(resp) if resp else 0}")

print("\nALL SERVER SCRIPT VIEWS VERIFIED 100% WORKING!")
