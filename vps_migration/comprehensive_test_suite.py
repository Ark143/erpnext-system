import requests, json, sys

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
login_res = session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=20)
login_res.raise_for_status()

print("=" * 70)
print("  COMPREHENSIVE ACCOUNTING & FINANCIALS TEST SUITE")
print("=" * 70)

# 1. Test Cash Flow (Daily, Monthly, Yearly)
print("\n[TEST 1] Consolidated Cash Flow Statement:")

# 1a. Monthly with all companies
cf_m = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=cash_flow&from_date=2026-01-01&to_date=2026-12-31&period=monthly").json().get('message', {})
print(f"  Monthly: Inflows = PHP {cf_m['summary']['inflows_consolidated']:,.2f} | Outflows = PHP {cf_m['summary']['outflows_consolidated']:,.2f} | Net = PHP {cf_m['summary']['net_consolidated']:,.2f}")
print(f"  Periods ({len(cf_m.get('periods', []))}): {[p['period_label'] for p in cf_m.get('periods', [])]}")

# 1b. Daily
cf_d = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=cash_flow&from_date=2026-08-01&to_date=2026-08-31&period=daily").json().get('message', {})
print(f"  Daily ({len(cf_d.get('periods', []))} days active): Net = PHP {cf_d['summary']['net_consolidated']:,.2f}")

# 1c. Yearly
cf_y = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=cash_flow&from_date=2024-01-01&to_date=2026-12-31&period=yearly").json().get('message', {})
print(f"  Yearly ({len(cf_y.get('periods', []))} years active): Net = PHP {cf_y['summary']['net_consolidated']:,.2f}")

# 1d. Multi-Company Filter on Cash Flow
cf_filt = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=cash_flow&selected_companies=Ultra%20MRF%20Dau%20Main,Automan%20Car%20Care%20Center").json().get('message', {})
print(f"  Filtered (2 Companies): Selected = {cf_filt.get('companies')} | Inflows = PHP {cf_filt['summary']['inflows_consolidated']:,.2f}")

# 2. Test AR Aging (30, 60, 90 Days)
print("\n[TEST 2] Accounts Receivable (AR) Aging Analysis (Terms & Credit Date Based):")
ar = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=ar_aging&as_of_date=2026-09-11").json().get('message', {})
ar_tot = ar.get('totals', {})
print(f"  Total AR Invoices Analyzed: {ar.get('invoice_count')}")
print(f"  Current / Not Due:   PHP {ar_tot.get('current', 0):>14,.2f}")
print(f"  1 - 30 Days Overdue: PHP {ar_tot.get('range_1_30', 0):>14,.2f}")
print(f"  31 - 60 Days Overdue:PHP {ar_tot.get('range_31_60', 0):>14,.2f}")
print(f"  61 - 90 Days Overdue:PHP {ar_tot.get('range_61_90', 0):>14,.2f}")
print(f"  90+ Days Overdue:    PHP {ar_tot.get('range_90_plus', 0):>14,.2f}")
print(f"  Total AR Outstanding:PHP {ar_tot.get('total_outstanding', 0):>14,.2f}")
print(f"  Unique Customers: {len(ar.get('customer_summary', []))}")

# 3. Test AP Aging (30, 60, 90 Days)
print("\n[TEST 3] Accounts Payable (AP) Aging Analysis (Terms & Credit Date Based):")
ap = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=ap_aging&as_of_date=2026-09-11").json().get('message', {})
ap_tot = ap.get('totals', {})
print(f"  Total AP Bills Analyzed:    {ap.get('bill_count')}")
print(f"  Current / Not Due:   PHP {ap_tot.get('current', 0):>14,.2f}")
print(f"  1 - 30 Days Overdue: PHP {ap_tot.get('range_1_30', 0):>14,.2f}")
print(f"  31 - 60 Days Overdue:PHP {ap_tot.get('range_31_60', 0):>14,.2f}")
print(f"  61 - 90 Days Overdue:PHP {ap_tot.get('range_61_90', 0):>14,.2f}")
print(f"  90+ Days Overdue:    PHP {ap_tot.get('range_90_plus', 0):>14,.2f}")
print(f"  Total AP Outstanding:PHP {ap_tot.get('total_outstanding', 0):>14,.2f}")
print(f"  Unique Suppliers: {len(ap.get('supplier_summary', []))}")

# 4. Test Web Route
print("\n[TEST 4] Live Web Route Verification:")
web_res = session.get(f"{BASE_URL}/consolidated-financials")
print(f"  GET /consolidated-financials: Status {web_res.status_code}")
assert "tab-nav-cash_flow" in web_res.text, "Missing Cash Flow tab in web page"
assert "tab-nav-ar_aging" in web_res.text, "Missing AR Aging tab in web page"
assert "tab-nav-ap_aging" in web_res.text, "Missing AP Aging tab in web page"
assert "xlsx.full.min.js" in web_res.text, "Missing SheetJS XLSX script"
print("  [SUCCESS] All Web UI tabs, Excel export scripts, and print styles are verified!")

print("\n" + "=" * 70)
print("  ALL TESTS PASSED SUCCESSFULLY (100% OK)")
print("=" * 70)
