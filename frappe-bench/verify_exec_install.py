import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
import json

frappe.init(site='erp.localhost')
frappe.connect()

print("=== 1. Test Server Script API Execution via Frappe ===")
frappe.form_dict = frappe._dict({'view': 'meta', 'company': 'Ultra MRF Dau Main'})
from frappe.core.doctype.server_script.server_script_utils import run_server_script_api
try:
    res = run_server_script_api('executive_dashboard')
    print("Server Script API Response:", frappe.response.get('message'))
except Exception as e:
    print("Server Script Execution note:", e)

print("\n=== 2. Test Direct Module Execution ===")
from vehicle_management.vehicle_management.executive_dashboard import executive_dashboard
meta = executive_dashboard(view='meta', company='Ultra MRF Dau Main')
print("Direct Meta:", meta)

exec_sum = executive_dashboard(view='exec_summary', company='Ultra MRF Dau Main')
print("Direct Exec Summary Revenue:", exec_sum['revenue'])

print("\n=== 3. Verify Web Page Document in DB ===")
wp = frappe.db.sql('SELECT name, route, published, LENGTH(main_section_html) as len FROM "tabWeb Page" WHERE name = %s', ('executive',), as_dict=True)
print("Web Page record:", wp)
