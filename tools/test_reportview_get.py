import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

# Let's test calling frappe.desk.reportview.get or testing frappe.utils.goal.get_monthly_results with various inputs
# We can test via frappe.client.get_list or check what works
res = s.get(f"{VPS_BASE}/api/method/frappe.desk.reportview.get", params={
    "doctype": "Sales Invoice",
    "fields": json.dumps(["TO_CHAR(posting_date, 'MM-YYYY') as month_year", "sum(base_grand_total) as total"]),
    "filters": json.dumps([["company", "=", "Automan Car Care Center"], ["docstatus", "=", 1]]),
    "group_by": "month_year"
})
print("reportview.get response:", res.status_code, res.text)
