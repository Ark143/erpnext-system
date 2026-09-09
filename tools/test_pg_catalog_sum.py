import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

pg_script = """
sql = '''
CREATE OR REPLACE FUNCTION pg_catalog.sum(unknown)
RETURNS numeric AS $$
    SELECT 0::numeric;
$$ LANGUAGE sql IMMUTABLE;
'''
try:
    frappe.db.sql(sql)
    frappe.db.commit()
    frappe.response['message'] = 'OK'
except Exception as e:
    frappe.response['message'] = str(e)
"""

s.put(f"{VPS_BASE}/api/resource/Server Script/VM%20PG%20Sum%20Fix", json={
    "script": pg_script,
    "script_type": "API",
    "api_method": "vm_pg_sum_fix",
    "allow_guest": 0,
    "disabled": 0
})

r = s.get(f"{VPS_BASE}/api/method/vm_pg_sum_fix")
print("Response from SQL execution:", r.status_code, r.text)

# Test Goal Graph API!
res_goal = s.get(f"{VPS_BASE}/api/method/frappe.utils.goal.get_monthly_goal_graph_data", params={
    "doctype": "Company",
    "docname": "Automan Car Care Center",
    "title": "Sales",
    "goal_value_field": "monthly_sales_target",
    "goal_total_field": "total_monthly_sales",
    "goal_history_field": "sales_monthly_history",
    "goal_doctype": "Sales Invoice",
    "goal_doctype_link": "company",
    "goal_field": "base_grand_total",
    "date_field": "posting_date",
    "filters": json.dumps({"docstatus": 1, "is_opening": ["!=", "Yes"]}),
    "aggregation": "sum"
})
print("Goal Graph API status:", res_goal.status_code)
print("Goal Graph API response:", json.dumps(res_goal.json(), indent=2))
