import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
from frappe.utils import now_datetime

frappe.init(site='erp.localhost')
frappe.connect()

now = now_datetime()

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
frappe.response["message"] = res
'''

script_name = "Executive Dashboard API"
exists = frappe.db.exists("Server Script", script_name)

if exists:
    frappe.db.sql(
        'UPDATE "tabServer Script" SET script=%s, script_type=%s, api_method=%s, allow_guest=1, disabled=0, modified=%s, modified_by=%s WHERE name=%s',
        (CLEAN_SERVER_SCRIPT, 'API', 'executive_dashboard', now, 'Administrator', script_name)
    )
    print(f"UPDATED Server Script: {script_name}")
else:
    frappe.db.sql(
        '''INSERT INTO "tabServer Script"
           (name, script_type, api_method, allow_guest, disabled, script, creation, modified, modified_by, owner, docstatus)
           VALUES (%s, %s, %s, 1, 0, %s, %s, %s, %s, %s, 0)''',
        (script_name, 'API', 'executive_dashboard', CLEAN_SERVER_SCRIPT, now, now, 'Administrator', 'Administrator')
    )
    print(f"CREATED Server Script: {script_name}")

frappe.db.commit()
frappe.clear_cache()
print("Updated Server Script!")
