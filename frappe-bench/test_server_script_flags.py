import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
from frappe.utils import now_datetime

frappe.init(site='erp.localhost')
frappe.connect()

CLEAN_SERVER_SCRIPT = '''
# Executive Dashboard Server Script API
view = frappe.form_dict.get("view") or "meta"
company = frappe.form_dict.get("company") or "Ultra MRF Dau Main"
months = frappe.form_dict.get("months") or 12
fy = frappe.form_dict.get("fy") or ""

res = frappe.call(
    "vehicle_management.vehicle_management.executive_dashboard.executive_dashboard",
    view=view,
    company=company,
    months=months,
    fy=fy
)
frappe.flags = res
'''

frappe.db.sql(
    'UPDATE "tabServer Script" SET script=%s, disabled=0 WHERE name=%s',
    (CLEAN_SERVER_SCRIPT, 'Executive Dashboard API')
)
frappe.db.commit()
frappe.clear_cache()

# Test execute_method
frappe.form_dict = frappe._dict({'view': 'meta', 'company': 'Ultra MRF Dau Main'})
from frappe.handler import run_server_script
resp = run_server_script('Executive Dashboard API')
print("run_server_script 'meta' result:", resp)

frappe.form_dict = frappe._dict({'view': 'exec_summary', 'company': 'Ultra MRF Dau Main', 'fy': '2026'})
resp2 = run_server_script('Executive Dashboard API')
print("run_server_script 'exec_summary' Revenue:", resp2.get('revenue'))
