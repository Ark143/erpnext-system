import requests
import json
import urllib.parse

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

history_data = {
    "09-2025": 145000.0,
    "10-2025": 162000.0,
    "11-2025": 178500.0,
    "12-2025": 210000.0,
    "01-2026": 155000.0,
    "02-2026": 168000.0,
    "03-2026": 182000.0,
    "04-2026": 175000.0,
    "05-2026": 190000.0,
    "06-2026": 185000.0,
    "07-2026": 192000.0,
    "08-2026": 195000.0,
    "09-2026": 198100.0
}

# Update Automan Car Care Center
res = s.put(f"{VPS_BASE}/api/resource/Company/Automan%20Car%20Care%20Center", json={
    "sales_monthly_history": json.dumps(history_data),
    "total_monthly_sales": 198100.0,
    "monthly_sales_target": 250000.0
})
print("Company update status:", res.status_code)

# Test the Goal Graph API!
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
print("\nGoal Graph API Status:", res_goal.status_code)
print("Goal Graph API Data:", json.dumps(res_goal.json(), indent=2))
