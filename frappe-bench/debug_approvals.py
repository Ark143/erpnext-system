import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
from frappe.handler import run_server_script

frappe.init(site='erp.localhost')
frappe.connect()

frappe.form_dict = frappe._dict({'view': 'approvals', 'company': 'Ultra MRF Dau Main'})
resp = run_server_script('Executive Dashboard API')
print("Approvals response via run_server_script:", resp)

from vehicle_management.vehicle_management.executive_dashboard import executive_dashboard
resp_mod = executive_dashboard(view='approvals', company='Ultra MRF Dau Main')
print("Approvals response via python module:", resp_mod)
