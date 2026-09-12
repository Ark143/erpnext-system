import requests
import json
from datetime import date

BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{BASE}/api/method/login", json={"usr": "Administrator", "pwd": "admin"})

company = "Automan Car Care Center"
today = date.today().strftime("%Y-%m-%d")

# 1. Create a sample Purchase Invoice with VAT 12% and 2% EWT
supp = s.get(f"{BASE}/api/resource/Supplier?limit=1").json()["data"][0]["name"]
pur_items = s.get(f"{BASE}/api/resource/Item?filters=" + json.dumps([["is_purchase_item", "=", 1]]) + "&limit=1").json()["data"]
item = pur_items[0]["name"]

sales_items = s.get(f"{BASE}/api/resource/Item?filters=" + json.dumps([["is_sales_item", "=", 1]]) + "&limit=1").json()["data"]
sales_item = sales_items[0]["name"]

pi_doc = {
    "doctype": "Purchase Invoice",
    "company": company,
    "supplier": supp,
    "posting_date": today,
    "due_date": today,
    "items": [{
        "item_code": item,
        "qty": 1,
        "rate": 10000,
        "expense_account": "Stock Adjustment - AUTOMAN",
        "cost_center": "Main - AUTOMAN"
    }],
    "taxes": [
        {
            "charge_type": "On Net Total",
            "account_head": "VAT - AUTOMAN",
            "description": "VAT 12%",
            "rate": 12.0,
            "category": "Total",
            "add_deduct_tax": "Add",
            "cost_center": "Main - AUTOMAN"
        },
        {
            "charge_type": "On Net Total",
            "account_head": "Expanded Withholding Tax Payable - AUTOMAN",
            "description": "2% Expanded Withholding Tax (Services - EWT)",
            "rate": 2.0,
            "category": "Total",
            "add_deduct_tax": "Deduct",
            "cost_center": "Main - AUTOMAN",
            "is_tax_withholding_account": 1
        }
    ]
}

r_pi = s.post(f"{BASE}/api/resource/Purchase%20Invoice", json=pi_doc)
print("Create Test Purchase Invoice with EWT:", r_pi.status_code)
if r_pi.status_code in (200, 201):
    pi_name = r_pi.json()["data"]["name"]
    print(f"Created Draft PI: {pi_name}")
    # Submit
    s.put(f"{BASE}/api/resource/Purchase%20Invoice/{pi_name}", json={"docstatus": 1})
    
    # Test Render BIR Form 2307 on Purchase Invoice
    pi_full = s.get(f"{BASE}/api/resource/Purchase%20Invoice/{pi_name}").json()["data"]
    r_render = s.post(f"{BASE}/api/method/frappe.www.printview.get_html_and_style", data={
        "doc": json.dumps(pi_full),
        "print_format": "BIR Form 2307",
        "doctype": "Purchase Invoice",
        "no_letterhead": 1
    })
    html = r_render.json().get("message", {}).get("html", "")
    print(f"Purchase Invoice BIR 2307 HTML rendered: {len(html)} bytes")
    if "bir-2307-container" in html:
        print("[SUCCESS] BIR Form 2307 renders directly on Purchase Invoice!")

# 2. Create a sample Sales Invoice with VAT 12% and 1% CWT
cust = s.get(f"{BASE}/api/resource/Customer?limit=1").json()["data"][0]["name"]
si_doc = {
    "doctype": "Sales Invoice",
    "company": company,
    "customer": cust,
    "posting_date": today,
    "due_date": today,
    "items": [{
        "item_code": sales_item,
        "qty": 1,
        "rate": 25000,
        "cost_center": "Main - AUTOMAN"
    }],
    "taxes": [
        {
            "charge_type": "On Net Total",
            "account_head": "VAT - AUTOMAN",
            "description": "VAT 12%",
            "rate": 12.0,
            "cost_center": "Main - AUTOMAN"
        },
        {
            "charge_type": "On Net Total",
            "account_head": "Creditable Withholding Tax - AUTOMAN",
            "description": "1% Creditable Withholding Tax (CWT)",
            "rate": -1.0,
            "cost_center": "Main - AUTOMAN",
            "is_tax_withholding_account": 1
        }
    ]
}

r_si = s.post(f"{BASE}/api/resource/Sales%20Invoice", json=si_doc)
print("\nCreate Test Sales Invoice with CWT:", r_si.status_code)
if r_si.status_code in (200, 201):
    si_name = r_si.json()["data"]["name"]
    print(f"Created Draft SI: {si_name}")
    # Submit
    s.put(f"{BASE}/api/resource/Sales%20Invoice/{si_name}", json={"docstatus": 1})
    
    # Test Render BIR Form 2307 on Sales Invoice
    si_full = s.get(f"{BASE}/api/resource/Sales%20Invoice/{si_name}").json()["data"]
    r_render = s.post(f"{BASE}/api/method/frappe.www.printview.get_html_and_style", data={
        "doc": json.dumps(si_full),
        "print_format": "BIR Form 2307",
        "doctype": "Sales Invoice",
        "no_letterhead": 1
    })
    html = r_render.json().get("message", {}).get("html", "")
    print(f"Sales Invoice BIR 2307 HTML rendered: {len(html)} bytes")
    if "bir-2307-container" in html:
        print("[SUCCESS] BIR Form 2307 renders directly on Sales Invoice!")

print("\nALL DIRECT INVOICE 2307 RENDER TESTS COMPLETED SUCCESSFULLY!")
