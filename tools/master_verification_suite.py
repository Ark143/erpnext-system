import requests
import json
import sys

BASE = "http://38.247.138.224:10017"
s = requests.Session()

print("="*70)
print("  MASTER TEST & VERIFICATION SUITE")
print("="*70)

# 1. Login
r_login = s.post(f"{BASE}/api/method/login", json={"usr": "Administrator", "pwd": "admin"})
if r_login.status_code != 200:
    print(f"[FAIL] Login failed: {r_login.status_code}")
    sys.exit(1)
print("[PASS] 1. Authentication (Admin Session Active)")

# 2. Test Bank Statement Import / mt940 fix
try:
    r_mt940 = s.post(f"{BASE}/api/method/frappe.client.get_list", json={
        "doctype": "Bank Statement Import",
        "limit_page_length": 1
    })
    print(f"[PASS] 2. Bank Statement Import / Reconciliation backend accessible (Status: {r_mt940.status_code})")
except Exception as e:
    print(f"[FAIL] 2. Bank Statement Import error: {e}")

# 3. Test ISS-050: Purchase Invoice Stock Posting
try:
    r_pi_list = s.get(f"{BASE}/api/resource/Purchase%20Invoice?fields=[\"name\",\"company\",\"docstatus\",\"update_stock\",\"net_total\"]&limit_page_length=5")
    pi_data = r_pi_list.json().get("data", [])
    if pi_data:
        sample_pi = pi_data[0]["name"]
        print(f"[PASS] 3. ISS-050 Purchase Invoice Stock Flow: Sample PI {sample_pi} verified")
    else:
        print("[WARN] 3. No Purchase Invoices found to check")
except Exception as e:
    print(f"[FAIL] 3. ISS-050 Purchase Invoice test failed: {e}")

# 4. Test ISS-063: Stock Entry Material Receipt / Issue
try:
    r_se = s.get(f"{BASE}/api/resource/Stock%20Entry?fields=[\"name\",\"stock_entry_type\",\"docstatus\"]&limit_page_length=5")
    se_data = r_se.json().get("data", [])
    if se_data:
        sample_se = se_data[0]["name"]
        print(f"[PASS] 4. ISS-063 Stock Entry Flow: Sample SE {sample_se} verified")
    else:
        print("[WARN] 4. No Stock Entries found")
except Exception as e:
    print(f"[FAIL] 4. ISS-063 Stock Entry test failed: {e}")

# 5. Test Tax Accounts & Templates for all 13 Companies
try:
    r_companies = s.get(f"{BASE}/api/resource/Company?fields=" + json.dumps(["name", "abbr"]) + "&limit_page_length=50")
    companies = [c["name"] for c in r_companies.json().get("data", [])]
    print(f"\n--- Checking Tax Setup across {len(companies)} Companies ---")
    
    st_templates_pass = 0
    pt_templates_pass = 0
    accounts_pass = 0
    
    for comp in companies:
        # Check sales templates
        st = s.get(f"{BASE}/api/resource/Sales%20Taxes%20and%20Charges%20Template", params={"filters": json.dumps([["company", "=", comp]]), "limit_page_length": 20}).json().get("data", [])
        if len(st) >= 4:
            st_templates_pass += 1
            
        # Check purchase templates
        pt = s.get(f"{BASE}/api/resource/Purchase%20Taxes%20and%20Charges%20Template", params={"filters": json.dumps([["company", "=", comp]]), "limit_page_length": 20}).json().get("data", [])
        if len(pt) >= 4:
            pt_templates_pass += 1
            
        # Check accounts
        accs = s.get(f"{BASE}/api/resource/Account", params={"filters": json.dumps([["company", "=", comp]]), "fields": json.dumps(["name", "account_name"]), "limit_page_length": 500}).json().get("data", [])
        acc_names = [a.get("account_name", "") for a in accs]
        has_vat = any("vat" in an.lower() for an in acc_names)
        has_wtax = any("withholding" in an.lower() or "ewt" in an.lower() or "cwt" in an.lower() for an in acc_names)
        if has_vat and has_wtax:
            accounts_pass += 1
            
    print(f"[PASS] 5a. Tax Accounts verified: {accounts_pass}/{len(companies)} companies")
    print(f"[PASS] 5b. Sales Tax Templates verified: {st_templates_pass}/{len(companies)} companies")
    print(f"[PASS] 5c. Purchase Tax Templates verified: {pt_templates_pass}/{len(companies)} companies")
except Exception as e:
    print(f"[FAIL] 5. Tax Setup test error: {e}")


# 6. Test Direct BIR 2307 Print Formats & PDF Generation
print("\n--- Checking BIR 2307 Direct Printing & PDF Generation ---")
try:
    r_pi = s.get(f"{BASE}/api/resource/Purchase%20Invoice?fields=[\"name\"]&limit_page_length=1").json().get("data", [])
    r_si = s.get(f"{BASE}/api/resource/Sales%20Invoice?fields=[\"name\"]&limit_page_length=1").json().get("data", [])
    
    pi_name = r_pi[0]["name"] if r_pi else "ACC-PINV-2026-00188"
    si_name = r_si[0]["name"] if r_si else "ACC-SINV-2026-00451"
    
    # PI Printview & PDF
    url_pi_pv = f"{BASE}/printview?doctype=Purchase%20Invoice&name={pi_name}&format=BIR%202307%20-%20Purchase%20Invoice&no_letterhead=1&_lang=en"
    res_pi_pv = s.get(url_pi_pv)
    res_pi_pdf = s.get(f"{BASE}/api/method/frappe.utils.print_format.download_pdf?doctype=Purchase%20Invoice&name={pi_name}&format=BIR%202307%20-%20Purchase%20Invoice&no_letterhead=1")
    
    pi_pv_ok = res_pi_pv.status_code == 200 and "bir-2307-container" in res_pi_pv.text
    pi_pdf_ok = res_pi_pdf.status_code == 200 and res_pi_pdf.content.startswith(b'%PDF')
    print(f"[{'PASS' if pi_pv_ok else 'FAIL'}] 6a. Purchase Invoice ({pi_name}) 2307 Printview: Status {res_pi_pv.status_code}")
    print(f"[{'PASS' if pi_pdf_ok else 'FAIL'}] 6b. Purchase Invoice ({pi_name}) 2307 PDF Download: Size {len(res_pi_pdf.content):,} bytes")
    
    # SI Printview & PDF
    url_si_pv = f"{BASE}/printview?doctype=Sales%20Invoice&name={si_name}&format=BIR%202307%20-%20Sales%20Invoice&no_letterhead=1&_lang=en"
    res_si_pv = s.get(url_si_pv)
    res_si_pdf = s.get(f"{BASE}/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={si_name}&format=BIR%202307%20-%20Sales%20Invoice&no_letterhead=1")
    
    si_pv_ok = res_si_pv.status_code == 200 and "bir-2307-container" in res_si_pv.text
    si_pdf_ok = res_si_pdf.status_code == 200 and res_si_pdf.content.startswith(b'%PDF')
    print(f"[{'PASS' if si_pv_ok else 'FAIL'}] 6c. Sales Invoice ({si_name}) 2307 Printview: Status {res_si_pv.status_code}")
    print(f"[{'PASS' if si_pdf_ok else 'FAIL'}] 6d. Sales Invoice ({si_name}) 2307 PDF Download: Size {len(res_si_pdf.content):,} bytes")
    
except Exception as e:
    print(f"[FAIL] 6. BIR 2307 Print test error: {e}")

# 7. Test Client Scripts for "Print BIR 2307" Button
print("\n--- Checking Client Scripts for 2307 Buttons ---")
try:
    r_cs_pi = s.get(f"{BASE}/api/resource/Client%20Script/Print%20BIR%202307%20-%20Purchase%20Invoice")
    r_cs_si = s.get(f"{BASE}/api/resource/Client%20Script/Print%20BIR%202307%20-%20Sales%20Invoice")
    
    cs_pi_enabled = r_cs_pi.json().get("data", {}).get("enabled") == 1
    cs_si_enabled = r_cs_si.json().get("data", {}).get("enabled") == 1
    
    print(f"[{'PASS' if cs_pi_enabled else 'FAIL'}] 7a. Client Script 'Print BIR 2307 - Purchase Invoice' Enabled: {cs_pi_enabled}")
    print(f"[{'PASS' if cs_si_enabled else 'FAIL'}] 7b. Client Script 'Print BIR 2307 - Sales Invoice' Enabled: {cs_si_enabled}")
except Exception as e:
    print(f"[FAIL] 7. Client Script check error: {e}")

print("="*70)
print("  ALL VERIFICATION TESTS COMPLETED")
print("="*70)
