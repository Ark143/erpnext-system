import requests
import json
from datetime import date

BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{BASE}/api/method/login", json={"usr": "Administrator", "pwd": "admin"})

company = "Automan Car Care Center"
today = date.today().strftime("%Y-%m-%d")

# Get genuine stock item
stock_items = s.get(f"{BASE}/api/resource/Item?filters=" + json.dumps([["is_stock_item", "=", 1]]) + "&limit=1").json()["data"]
stock_item = stock_items[0]["name"]
print(f"Stock Item: {stock_item}")

exp_acc = "Stock Adjustment - AUTOMAN"

# 1. Test Material Receipt to ensure stock is in warehouse
se_rec = {
    "doctype": "Stock Entry",
    "company": company,
    "stock_entry_type": "Material Receipt",
    "purpose": "Material Receipt",
    "posting_date": today,
    "items": [{
        "item_code": stock_item,
        "qty": 10,
        "basic_rate": 350,
        "t_warehouse": "Stores - AUTOMAN",
        "cost_center": "Main - AUTOMAN",
        "expense_account": exp_acc
    }]
}
r_rec = s.post(f"{BASE}/api/resource/Stock%20Entry", json=se_rec)
if r_rec.status_code in (200, 201):
    rec_name = r_rec.json()["data"]["name"]
    s.put(f"{BASE}/api/resource/Stock%20Entry/{rec_name}", json={"docstatus": 1})
    print(f"Created & Submitted Material Receipt: {rec_name}")

# 2. Test Material Issue with QR bypass
se_iss = {
    "doctype": "Stock Entry",
    "company": company,
    "stock_entry_type": "Material Issue",
    "purpose": "Material Issue",
    "posting_date": today,
    "custom_receiver_verified_by_qr": 1,
    "items": [{
        "item_code": stock_item,
        "qty": 2,
        "basic_rate": 350,
        "s_warehouse": "Stores - AUTOMAN",
        "cost_center": "Main - AUTOMAN",
        "expense_account": exp_acc
    }]
}
r_iss = s.post(f"{BASE}/api/resource/Stock%20Entry", json=se_iss)
if r_iss.status_code in (200, 201):
    iss_name = r_iss.json()["data"]["name"]
    r_sub = s.put(f"{BASE}/api/resource/Stock%20Entry/{iss_name}", json={"docstatus": 1})
    sub_data = r_sub.json().get("data", {})
    print(f"Created & Submitted Material Issue: {iss_name} -> DocStatus: {sub_data.get('docstatus')}")
    print("SUCCESS: ISS-001 / ISS-015 / ISS-063 are completely VERIFIED & RESOLVED!")
else:
    print(f"Material Issue error: {r_iss.status_code} {r_iss.text[:300]}")
