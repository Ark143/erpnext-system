import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

# 1. Ensure Global Defaults and User Defaults are set
s.put(f"{VPS_BASE}/api/resource/Global Defaults/Global Defaults", json={
    "default_company": "Automan Car Care Center"
})
s.post(f"{VPS_BASE}/api/method/frappe.client.set_default", json={
    "key": "company",
    "value": "Automan Car Care Center",
    "parent": "Administrator"
})
s.post(f"{VPS_BASE}/api/method/frappe.client.set_default", json={
    "key": "Company",
    "value": "Automan Car Care Center"
})

# 2. Test Sales Order Trends with full filters
res1 = s.get(f"{VPS_BASE}/api/method/frappe.desk.query_report.run", params={
    "report_name": "Sales Order Trends",
    "filters": json.dumps({
        "company": "Automan Car Care Center",
        "fiscal_year": "2026",
        "period": "Monthly",
        "based_on": "Item"
    })
})
print("1. Sales Order Trends (with filters): Status", res1.status_code)
if res1.status_code == 200:
    cols = len(res1.json().get("message", {}).get("columns", []))
    rows = len(res1.json().get("message", {}).get("result", []))
    print(f"   -> Columns: {cols}, Rows: {rows}")
else:
    print("   -> Error:", res1.text[:200])

# 3. Test Sales Order Trends with partial/default filters
res2 = s.get(f"{VPS_BASE}/api/method/frappe.desk.query_report.run", params={
    "report_name": "Sales Order Trends",
    "filters": json.dumps({
        "company": "Automan Car Care Center"
    })
})
print("\n2. Sales Order Trends (partial filters): Status", res2.status_code)
if res2.status_code == 200:
    print("   -> Success!")
else:
    print("   -> Error:", res2.text[:200])

# 4. Test other trend reports
for rep_name in ["Purchase Order Trends", "Sales Analytics", "Item-wise Sales History"]:
    try:
        r = s.get(f"{VPS_BASE}/api/method/frappe.desk.query_report.run", params={
            "report_name": rep_name,
            "filters": json.dumps({"company": "Automan Car Care Center"})
        })
        print(f"\n{rep_name}: Status {r.status_code}")
    except Exception as e:
        print(f"\n{rep_name}: Exception {e}")
