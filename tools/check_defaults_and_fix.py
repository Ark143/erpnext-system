import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

# 1. Check Global Defaults
gd = s.get(f"{VPS_BASE}/api/resource/Global Defaults/Global Defaults").json().get("data", {})
print("Global Defaults default_company:", gd.get("default_company"))
print("Global Defaults default_currency:", gd.get("default_currency"))

# 2. Update Global Defaults default_company to "Automan Car Care Center" or "ULTRA MRF"
if not gd.get("default_company"):
    res = s.put(f"{VPS_BASE}/api/resource/Global Defaults/Global Defaults", json={
        "default_company": "Automan Car Care Center"
    })
    print("Updated Global Defaults default_company:", res.status_code)

# 3. Set user default for Administrator
res_def = s.post(f"{VPS_BASE}/api/method/frappe.client.set_default", json={
    "key": "company",
    "value": "Automan Car Care Center",
    "parent": "Administrator"
})
print("Set user default for Administrator:", res_def.status_code, res_def.text)

# Also set global default
res_gdef = s.post(f"{VPS_BASE}/api/method/frappe.client.set_default", json={
    "key": "Company",
    "value": "Automan Car Care Center"
})
print("Set global default for Company:", res_gdef.status_code, res_gdef.text)

# 4. Test running Sales Order Trends report
res_rep = s.get(f"{VPS_BASE}/api/method/frappe.desk.query_report.run", params={
    "report_name": "Sales Order Trends",
    "filters": json.dumps({
        "company": "Automan Car Care Center",
        "fiscal_year": "2026-2027",
        "period": "Monthly",
        "based_on": "Item"
    })
})
print("Sales Order Trends report with company filter:", res_rep.status_code)
if res_rep.status_code == 200:
    print("Report rows count:", len(res_rep.json().get("message", {}).get("result", [])))
else:
    print("Report error:", res_rep.text)

# 5. Test running report with empty filters (like when first clicking report in desk)
res_rep_empty = s.get(f"{VPS_BASE}/api/method/frappe.desk.query_report.run", params={
    "report_name": "Sales Order Trends",
    "filters": "{}"
})
print("Sales Order Trends report with empty filters:", res_rep_empty.status_code)
if res_rep_empty.status_code != 200:
    print("Empty filters error:", res_rep_empty.text)
