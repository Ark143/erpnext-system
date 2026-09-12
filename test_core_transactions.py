import requests
import json
from datetime import date, timedelta

BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{BASE}/api/method/login", json={"usr": "Administrator", "pwd": "admin"})

company = "Automan Car Care Center"
today = date.today().strftime("%Y-%m-%d")
delivery_date = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")

# Get Customer, Item, Supplier, Warehouse
cust = s.get(f"{BASE}/api/resource/Customer?limit=1").json()["data"][0]["name"]
item = s.get(f"{BASE}/api/resource/Item?limit=1").json()["data"][0]["name"]
supp = s.get(f"{BASE}/api/resource/Supplier?limit=1").json()["data"][0]["name"]

# Get Company Warehouse & Cost Center
wh_res = s.get(f"{BASE}/api/resource/Warehouse?filters=" + json.dumps([["company", "=", company], ["is_group", "=", 0]]))
warehouse = wh_res.json()["data"][0]["name"] if wh_res.json().get("data") else "Stores - AUTOMAN"

cc_res = s.get(f"{BASE}/api/resource/Cost%20Center?filters=" + json.dumps([["company", "=", company], ["is_group", "=", 0]]))
cost_center = cc_res.json()["data"][0]["name"] if cc_res.json().get("data") else "Main - AUTOMAN"

print(f"Test Parameters:\nCompany: {company}\nCustomer: {cust}\nSupplier: {supp}\nItem: {item}\nWarehouse: {warehouse}\nCost Center: {cost_center}\n")

# ── 1. TEST SALES ORDER (ISS-004) ──────────────────────────────────
print("--- [1] Testing Sales Order (ISS-004) ---")
so_doc = {
    "doctype": "Sales Order",
    "company": company,
    "customer": cust,
    "transaction_date": today,
    "delivery_date": delivery_date,
    "order_type": "Sales",
    "items": [{
        "item_code": item,
        "qty": 1,
        "rate": 500,
        "delivery_date": delivery_date,
        "warehouse": warehouse
    }]
}
r_so = s.post(f"{BASE}/api/resource/Sales%20Order", json=so_doc)
if r_so.status_code in (200, 201):
    so_name = r_so.json()["data"]["name"]
    print(f"Created Draft Sales Order: {so_name}")
    # Submit
    r_sub = s.put(f"{BASE}/api/resource/Sales%20Order/{so_name}", json={"docstatus": 1})
    if r_sub.status_code in (200, 201):
        print(f"SUCCESS: Sales Order {so_name} SUBMITTED successfully! (ISS-004 PASS)")
    else:
        print(f"FAIL on Sales Order submit: {r_sub.status_code} {r_sub.text[:400]}")
else:
    print(f"FAIL on Sales Order create: {r_so.status_code} {r_so.text[:400]}")

print()

# ── 2. TEST PURCHASE INVOICE (ISS-050) ─────────────────────────────
print("--- [2] Testing Purchase Invoice (ISS-050) ---")
# Get expense account
exp_acc_res = s.get(f"{BASE}/api/resource/Account?filters=" + json.dumps([["company", "=", company], ["account_type", "=", "Expense Account"], ["is_group", "=", 0]]))
exp_acc = exp_acc_res.json()["data"][0]["name"] if exp_acc_res.json().get("data") else "Cost of Goods Sold - AUTOMAN"

pi_doc = {
    "doctype": "Purchase Invoice",
    "company": company,
    "supplier": supp,
    "posting_date": today,
    "due_date": today,
    "update_stock": 1,
    "items": [{
        "item_code": item,
        "qty": 1,
        "rate": 300,
        "expense_account": exp_acc,
        "cost_center": cost_center,
        "warehouse": warehouse
    }]
}
r_pi = s.post(f"{BASE}/api/resource/Purchase%20Invoice", json=pi_doc)
if r_pi.status_code in (200, 201):
    pi_name = r_pi.json()["data"]["name"]
    print(f"Created Draft Purchase Invoice: {pi_name}")
    # Submit
    r_sub = s.put(f"{BASE}/api/resource/Purchase%20Invoice/{pi_name}", json={"docstatus": 1})
    if r_sub.status_code in (200, 201):
        print(f"SUCCESS: Purchase Invoice {pi_name} SUBMITTED with update_stock=1! (ISS-050 PASS)")
    else:
        print(f"FAIL on Purchase Invoice submit: {r_sub.status_code} {r_sub.text[:400]}")
else:
    print(f"FAIL on Purchase Invoice create: {r_pi.status_code} {r_pi.text[:400]}")

print()

# ── 3. TEST STOCK ENTRY (ISS-063) ──────────────────────────────────
print("--- [3] Testing Stock Entry (ISS-063) ---")
se_doc = {
    "doctype": "Stock Entry",
    "company": company,
    "stock_entry_type": "Material Receipt",
    "purpose": "Material Receipt",
    "posting_date": today,
    "custom_receiver_verified_by_qr": 1,
    "items": [{
        "item_code": item,
        "qty": 2,
        "basic_rate": 300,
        "t_warehouse": warehouse,
        "cost_center": cost_center
    }]
}
r_se = s.post(f"{BASE}/api/resource/Stock%20Entry", json=se_doc)
if r_se.status_code in (200, 201):
    se_name = r_se.json()["data"]["name"]
    print(f"Created Draft Stock Entry: {se_name}")
    # Submit
    r_sub = s.put(f"{BASE}/api/resource/Stock%20Entry/{se_name}", json={"docstatus": 1})
    if r_sub.status_code in (200, 201):
        print(f"SUCCESS: Stock Entry {se_name} SUBMITTED successfully! (ISS-063 PASS)")
    else:
        print(f"FAIL on Stock Entry submit: {r_sub.status_code} {r_sub.text[:400]}")
else:
    print(f"FAIL on Stock Entry create: {r_se.status_code} {r_se.text[:400]}")
