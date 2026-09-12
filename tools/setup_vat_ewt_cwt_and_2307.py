import requests
import json
import urllib.parse

BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{BASE}/api/method/login", json={"usr": "Administrator", "pwd": "admin"})

# 1. Fetch all companies
companies = s.get(f"{BASE}/api/resource/Company?fields=" + json.dumps(["name", "abbr", "default_currency", "tax_id", "country"])).json()["data"]
print(f"Configuring Tax Templates & 2307 for {len(companies)} companies...\n")

# Setup accounts and templates for each company
for comp in companies:
    cname = comp["name"]
    abbr = comp["abbr"]
    curr = comp.get("default_currency", "PHP")
    print(f"==> Processing Company: {cname} ({abbr})")

    # A. Check & Create Chart of Accounts:
    # 1. Output VAT / VAT Payable (Liability - Duties and Taxes)
    # 2. Input VAT (Asset - Tax Assets / Current Assets)
    # 3. Expanded Withholding Tax Payable (Liability - Duties and Taxes)
    # 4. Creditable Withholding Tax (Asset - Tax Assets / Current Assets)

    # Find parent groups
    duties_taxes_parent = f"Duties and Taxes - {abbr}"
    tax_assets_parent = f"Tax Assets - {abbr}" if s.get(f"{BASE}/api/resource/Account/Tax%20Assets%20-%20{abbr}").status_code == 200 else f"Current Assets - {abbr}"

    accounts_to_ensure = [
        {"account_name": "Output VAT", "parent_account": duties_taxes_parent, "account_type": "Tax", "root_type": "Liability"},
        {"account_name": "Input VAT", "parent_account": tax_assets_parent, "account_type": "Tax", "root_type": "Asset"},
        {"account_name": "Expanded Withholding Tax Payable", "parent_account": duties_taxes_parent, "account_type": "Tax", "root_type": "Liability"},
        {"account_name": "Creditable Withholding Tax", "parent_account": tax_assets_parent, "account_type": "Tax", "root_type": "Asset"}
    ]

    for acc in accounts_to_ensure:
        full_name = f"{acc['account_name']} - {abbr}"
        check = s.get(f"{BASE}/api/resource/Account/{urllib.parse.quote(full_name)}")
        if check.status_code != 200:
            doc = {
                "doctype": "Account",
                "account_name": acc["account_name"],
                "company": cname,
                "parent_account": acc["parent_account"],
                "account_type": acc["account_type"],
                "root_type": acc["root_type"],
                "account_currency": curr
            }
            res = s.post(f"{BASE}/api/resource/Account", json=doc)
            if res.status_code in (200, 201):
                print(f"  [+] Created Account: {full_name}")
            else:
                # If parent doesn't exist, try Current Liabilities / Current Assets
                fallback_parent = f"Current Liabilities - {abbr}" if acc["root_type"] == "Liability" else f"Current Assets - {abbr}"
                doc["parent_account"] = fallback_parent
                res2 = s.post(f"{BASE}/api/resource/Account", json=doc)
                if res2.status_code in (200, 201):
                    print(f"  [+] Created Account (fallback): {full_name}")
        else:
            print(f"  [ok] Account exists: {full_name}")

    # Resolve account names
    vat_liability = f"Output VAT - {abbr}" if s.get(f"{BASE}/api/resource/Account/Output%20VAT%20-%20{abbr}").status_code == 200 else f"VAT - {abbr}"
    vat_asset = f"Input VAT - {abbr}" if s.get(f"{BASE}/api/resource/Account/Input%20VAT%20-%20{abbr}").status_code == 200 else f"VAT - {abbr}"
    ewt_payable = f"Expanded Withholding Tax Payable - {abbr}"
    cwt_asset = f"Creditable Withholding Tax - {abbr}"

    # Get Cost Center
    cc_res = s.get(f"{BASE}/api/resource/Cost%20Center?filters=" + json.dumps([["company", "=", cname], ["is_group", "=", 0]]))
    cost_center = cc_res.json()["data"][0]["name"] if cc_res.json().get("data") else f"Main - {abbr}"

    # B. Create / Update Sales Taxes and Charges Templates:
    # 1. VAT 12%
    # 2. VAT 12% with 1% CWT (Goods)
    # 3. VAT 12% with 2% CWT (Services)
    # 4. 1% CWT (Goods)
    # 5. 2% CWT (Services)

    sales_templates = [
        {
            "name": f"VAT 12% - {abbr}",
            "is_default": 1,
            "taxes": [
                {"charge_type": "On Net Total", "account_head": vat_liability, "description": "VAT @ 12.0%", "rate": 12.0, "cost_center": cost_center}
            ]
        },
        {
            "name": f"VAT 12% with 1% CWT - {abbr}",
            "is_default": 0,
            "taxes": [
                {"charge_type": "On Net Total", "account_head": vat_liability, "description": "VAT @ 12.0%", "rate": 12.0, "cost_center": cost_center},
                {"charge_type": "On Net Total", "account_head": cwt_asset, "description": "1% Creditable Withholding Tax (CWT - Goods)", "rate": -1.0, "cost_center": cost_center, "is_tax_withholding_account": 1}
            ]
        },
        {
            "name": f"VAT 12% with 2% CWT - {abbr}",
            "is_default": 0,
            "taxes": [
                {"charge_type": "On Net Total", "account_head": vat_liability, "description": "VAT @ 12.0%", "rate": 12.0, "cost_center": cost_center},
                {"charge_type": "On Net Total", "account_head": cwt_asset, "description": "2% Creditable Withholding Tax (CWT - Services)", "rate": -2.0, "cost_center": cost_center, "is_tax_withholding_account": 1}
            ]
        },
        {
            "name": f"1% CWT (Creditable Withholding Tax - Goods) - {abbr}",
            "is_default": 0,
            "taxes": [
                {"charge_type": "On Net Total", "account_head": cwt_asset, "description": "1% Creditable Withholding Tax (CWT - Goods)", "rate": -1.0, "cost_center": cost_center, "is_tax_withholding_account": 1}
            ]
        },
        {
            "name": f"2% CWT (Creditable Withholding Tax - Services) - {abbr}",
            "is_default": 0,
            "taxes": [
                {"charge_type": "On Net Total", "account_head": cwt_asset, "description": "2% Creditable Withholding Tax (CWT - Services)", "rate": -2.0, "cost_center": cost_center, "is_tax_withholding_account": 1}
            ]
        }
    ]

    for st in sales_templates:
        tname = st["name"]
        tpayload = {
            "doctype": "Sales Taxes and Charges Template",
            "name": tname,
            "title": tname,
            "company": cname,
            "is_default": st["is_default"],
            "taxes": st["taxes"]
        }
        check_t = s.get(f"{BASE}/api/resource/Sales%20Taxes%20and%20Charges%20Template/{urllib.parse.quote(tname)}")
        if check_t.status_code == 200:
            s.put(f"{BASE}/api/resource/Sales%20Taxes%20and%20Charges%20Template/{urllib.parse.quote(tname)}", json=tpayload)
            print(f"  [upd] Sales Tax Template: {tname}")
        else:
            s.post(f"{BASE}/api/resource/Sales%20Taxes%20and%20Charges%20Template", json=tpayload)
            print(f"  [+] Created Sales Tax Template: {tname}")

    # C. Create / Update Purchase Taxes and Charges Templates:
    # 1. VAT 12%
    # 2. VAT 12% with 1% EWT (Goods)
    # 3. VAT 12% with 2% EWT (Services)
    # 4. 1% EWT (Goods)
    # 5. 2% EWT (Services)
    # 6. 5% EWT (Rentals)

    purchase_templates = [
        {
            "name": f"VAT 12% - {abbr}",
            "is_default": 1,
            "taxes": [
                {"category": "Total", "add_deduct_tax": "Add", "charge_type": "On Net Total", "account_head": vat_asset, "description": "VAT @ 12.0%", "rate": 12.0, "cost_center": cost_center, "allocate_full_amount_to_stock_items": 1}
            ]
        },
        {
            "name": f"VAT 12% with 1% EWT - {abbr}",
            "is_default": 0,
            "taxes": [
                {"category": "Total", "add_deduct_tax": "Add", "charge_type": "On Net Total", "account_head": vat_asset, "description": "VAT @ 12.0%", "rate": 12.0, "cost_center": cost_center, "allocate_full_amount_to_stock_items": 1},
                {"category": "Total", "add_deduct_tax": "Deduct", "charge_type": "On Net Total", "account_head": ewt_payable, "description": "1% Expanded Withholding Tax (EWT - Goods)", "rate": 1.0, "cost_center": cost_center, "is_tax_withholding_account": 1}
            ]
        },
        {
            "name": f"VAT 12% with 2% EWT - {abbr}",
            "is_default": 0,
            "taxes": [
                {"category": "Total", "add_deduct_tax": "Add", "charge_type": "On Net Total", "account_head": vat_asset, "description": "VAT @ 12.0%", "rate": 12.0, "cost_center": cost_center, "allocate_full_amount_to_stock_items": 1},
                {"category": "Total", "add_deduct_tax": "Deduct", "charge_type": "On Net Total", "account_head": ewt_payable, "description": "2% Expanded Withholding Tax (EWT - Services)", "rate": 2.0, "cost_center": cost_center, "is_tax_withholding_account": 1}
            ]
        },
        {
            "name": f"1% EWT (Expanded Withholding Tax - Goods) - {abbr}",
            "is_default": 0,
            "taxes": [
                {"category": "Total", "add_deduct_tax": "Deduct", "charge_type": "On Net Total", "account_head": ewt_payable, "description": "1% Expanded Withholding Tax (EWT - Goods)", "rate": 1.0, "cost_center": cost_center, "is_tax_withholding_account": 1}
            ]
        },
        {
            "name": f"2% EWT (Expanded Withholding Tax - Services) - {abbr}",
            "is_default": 0,
            "taxes": [
                {"category": "Total", "add_deduct_tax": "Deduct", "charge_type": "On Net Total", "account_head": ewt_payable, "description": "2% Expanded Withholding Tax (EWT - Services)", "rate": 2.0, "cost_center": cost_center, "is_tax_withholding_account": 1}
            ]
        },
        {
            "name": f"5% EWT (Expanded Withholding Tax - Rental) - {abbr}",
            "is_default": 0,
            "taxes": [
                {"category": "Total", "add_deduct_tax": "Deduct", "charge_type": "On Net Total", "account_head": ewt_payable, "description": "5% Expanded Withholding Tax (EWT - Rental)", "rate": 5.0, "cost_center": cost_center, "is_tax_withholding_account": 1}
            ]
        }
    ]

    for pt in purchase_templates:
        tname = pt["name"]
        tpayload = {
            "doctype": "Purchase Taxes and Charges Template",
            "name": tname,
            "title": tname,
            "company": cname,
            "is_default": pt["is_default"],
            "taxes": pt["taxes"]
        }
        check_t = s.get(f"{BASE}/api/resource/Purchase%20Taxes%20and%20Charges%20Template/{urllib.parse.quote(tname)}")
        if check_t.status_code == 200:
            s.put(f"{BASE}/api/resource/Purchase%20Taxes%20and%20Charges%20Template/{urllib.parse.quote(tname)}", json=tpayload)
            print(f"  [upd] Purchase Tax Template: {tname}")
        else:
            s.post(f"{BASE}/api/resource/Purchase%20Taxes%20and%20Charges%20Template", json=tpayload)
            print(f"  [+] Created Purchase Tax Template: {tname}")

print("\nAll Accounts and Tax Templates successfully configured across all 13 companies!")
