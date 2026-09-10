import requests
import json
import urllib.parse
import time
from datetime import datetime

VPS_BASE = "http://38.247.138.224:10017"

s = requests.Session()
login_res = s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

results = {
    "timestamp": datetime.now().isoformat(),
    "target": VPS_BASE,
    "tests_run": 0,
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "details": [],
    "issues": []
}

def log_test(category, name, passed, detail="", is_warning=False):
    results["tests_run"] += 1
    status_str = "PASS" if passed else ("WARNING" if is_warning else "FAIL")
    if passed:
        results["passed"] += 1
    elif is_warning:
        results["warnings"] += 1
    else:
        results["failed"] += 1
        
    res_entry = {
        "category": category,
        "name": name,
        "status": status_str,
        "detail": detail
    }
    results["details"].append(res_entry)
    
    if not passed and not is_warning:
        results["issues"].append({
            "id": f"ISS-INT-{len(results['issues'])+1:03d}",
            "category": category,
            "title": name,
            "detail": detail
        })
    print(f"[{status_str:<7}] {category:<20} | {name:<45} | {str(detail)[:60]}")

print("================================================================================")
print("STARTING COMPREHENSIVE ERPNEXT & VMS SYSTEM INTEGRITY AUDIT")
print("================================================================================")

# -----------------------------------------------------------------------------
# 1. AUTHENTICATION & CORE CONNECTIVITY
# -----------------------------------------------------------------------------
log_test("Auth", "Administrator Session Login", login_res.status_code == 200, f"Status: {login_res.status_code}")

# -----------------------------------------------------------------------------
# 2. MASTER DATA INTEGRITY
# -----------------------------------------------------------------------------
try:
    r = s.get(f"{VPS_BASE}/api/resource/Company?limit_page_length=50")
    comps = [c['name'] for c in r.json().get('data', [])]
    log_test("Master Data", "Active Companies Check", len(comps) >= 11, f"Found {len(comps)} companies: {', '.join(comps[:4])}...")
except Exception as e:
    log_test("Master Data", "Active Companies Check", False, str(e))

try:
    r = s.get(f"{VPS_BASE}/api/resource/Item?limit_page_length=10")
    items = r.json().get('data', [])
    log_test("Master Data", "Item Master Records", len(items) > 0, f"Fetched {len(items)} sample items")
except Exception as e:
    log_test("Master Data", "Item Master Records", False, str(e))

try:
    r = s.get(f"{VPS_BASE}/api/resource/Customer Vehicle?limit_page_length=5")
    vehs = r.json().get('data', [])
    log_test("Master Data", "Customer Vehicle Registry", len(vehs) > 0, f"Sample vehicle: {vehs[0]['name'] if vehs else 'None'}")
except Exception as e:
    log_test("Master Data", "Customer Vehicle Registry", False, str(e))

try:
    r = s.get(f"{VPS_BASE}/api/resource/Bin Location?limit_page_length=10")
    bins = r.json().get('data', [])
    log_test("Master Data", "Warehouse Bin Locations", len(bins) > 0, f"Found {len(bins)} bin location records")
except Exception as e:
    log_test("Master Data", "Warehouse Bin Locations", False, str(e))

# -----------------------------------------------------------------------------
# 3. NOTIFICATION & OPEN COUNT APIs (Postgres Safe)
# -----------------------------------------------------------------------------
test_items = ['SRV-ELEC-CHECK', 'PMS', 'PMS-OIL', 'TE37-18X8.5-BRONZE', 'ACC-SRV-001']
for itm in test_items:
    try:
        r = s.get(f"{VPS_BASE}/api/method/frappe.desk.notifications.get_open_count", params={
            "doctype": "Item",
            "name": itm,
            "items": json.dumps(["BOM", "Sales Order", "Sales Invoice", "Delivery Note", "Stock Entry"])
        })
        log_test("Notifications", f"Item Open Count ({itm})", r.status_code == 200, f"Status: {r.status_code}")
    except Exception as e:
        log_test("Notifications", f"Item Open Count ({itm})", False, str(e))

# -----------------------------------------------------------------------------
# 4. VEHICLE MANAGEMENT ANALYTICS & PERMISSIONS
# -----------------------------------------------------------------------------
try:
    r_perm = s.get(f"{VPS_BASE}/api/method/vehicle_management.vehicle_management.analytics.get_user_analytics_permissions")
    p_data = r_perm.json().get('message', {})
    log_test("VMS Analytics", "Admin Analytics Permissions", p_data.get('can_view_all') == True, f"Can view all: {p_data.get('can_view_all')}, Allowed: {len(p_data.get('allowed_companies', []))}")
except Exception as e:
    log_test("VMS Analytics", "Admin Analytics Permissions", False, str(e))

try:
    r_ana = s.get(f"{VPS_BASE}/api/method/vehicle_management.vehicle_management.analytics.get_vehicle_management_analytics", params={
        "company": "All Companies",
        "timespan": "Last 30 Days"
    })
    a_data = r_ana.json().get('message', {})
    rev = a_data.get('summary', {}).get('total_revenue', 0)
    jos = a_data.get('summary', {}).get('total_jos', 0)
    log_test("VMS Analytics", "Analytics Dashboard Data", r_ana.status_code == 200 and rev > 0, f"Revenue: PHP {rev:,.2f} | JOs: {jos}")
except Exception as e:
    log_test("VMS Analytics", "Analytics Dashboard Data", False, str(e))

# -----------------------------------------------------------------------------
# 5. GOAL GRAPH AGGREGATION API (Postgres Sum/Date Fix)
# -----------------------------------------------------------------------------
try:
    r_goal = s.get(f"{VPS_BASE}/api/method/frappe.utils.goal.get_monthly_goal_graph_data", params={
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
    log_test("Goal API", "Automan Goal Sales Graph", r_goal.status_code == 200, f"Status: {r_goal.status_code}")
except Exception as e:
    log_test("Goal API", "Automan Goal Sales Graph", False, str(e))

# -----------------------------------------------------------------------------
# 6. REPORTS EXECUTION (Postgres Compatibility Check)
# -----------------------------------------------------------------------------
reports_to_test = [
    ("Sales Order Trends", {"company": "Automan Car Care Center", "fiscal_year": "2026", "period": "Monthly", "based_on": "Item"}),
    ("General Ledger", {"company": "Automan Car Care Center", "from_date": "2026-01-01", "to_date": "2026-12-31"}),
    ("Accounts Receivable", {"company": "Automan Car Care Center", "report_date": "2026-09-10"}),
    ("Accounts Payable", {"company": "Automan Car Care Center", "report_date": "2026-09-10"}),
    ("Stock Balance", {"company": "Automan Car Care Center", "from_date": "2026-01-01", "to_date": "2026-12-31"}),
    ("Stock Ledger", {"company": "Automan Car Care Center", "from_date": "2026-01-01", "to_date": "2026-12-31"}),
    ("Profit and Loss Statement", {"company": "Automan Car Care Center", "filter_based_on": "Fiscal Year", "from_fiscal_year": "2026", "to_fiscal_year": "2026", "periodicity": "Monthly"}),
    ("Balance Sheet", {"company": "Automan Car Care Center", "filter_based_on": "Fiscal Year", "from_fiscal_year": "2026", "to_fiscal_year": "2026", "periodicity": "Monthly"})
]

for rep_name, rep_filters in reports_to_test:
    try:
        r_rep = s.get(f"{VPS_BASE}/api/method/frappe.desk.query_report.run", params={
            "report_name": rep_name,
            "filters": json.dumps(rep_filters)
        })
        is_ok = r_rep.status_code == 200 and "message" in r_rep.json()
        res_len = len(r_rep.json().get('message', {}).get('result', [])) if is_ok else 0
        log_test("Reports", f"Report: {rep_name}", is_ok, f"Status: {r_rep.status_code} | Rows: {res_len}")
    except Exception as e:
        log_test("Reports", f"Report: {rep_name}", False, str(e))

# -----------------------------------------------------------------------------
# 7. PHILIPPINE BIR SUITE INTEGRITY
# -----------------------------------------------------------------------------
bir_doctypes = [
    "BIR Sales Journal",
    "BIR Purchases Book",
    "BIR Cash Receipt Journal",
    "BIR Cash Disbursement Journal",
    "BIR General Journal",
    "BIR General Ledger",
    "BIR Form 2307",
    "BIR VAT Summary",
    "BIR Withholding Summary"
]

for b_dt in bir_doctypes:
    try:
        r_b = s.get(f"{VPS_BASE}/api/resource/{urllib.parse.quote(b_dt)}?limit_page_length=5")
        log_test("BIR Suite", f"DocType: {b_dt}", r_b.status_code == 200, f"Status: {r_b.status_code} | Count: {len(r_b.json().get('data', []))}")
    except Exception as e:
        log_test("BIR Suite", f"DocType: {b_dt}", False, str(e))

# -----------------------------------------------------------------------------
# 8. ERROR LOG AUDIT (Checking for live errors on VPS)
# -----------------------------------------------------------------------------
try:
    r_err = s.get(f"{VPS_BASE}/api/resource/Error Log?limit_page_length=15&order_by=creation desc")
    err_list = r_err.json().get('data', [])
    log_test("System Health", "Error Log Audit", True, f"Found {len(err_list)} recent error entries")
    if err_list:
        print("\n--- Recent Error Logs on VPS ---")
        for err in err_list[:5]:
            err_doc = s.get(f"{VPS_BASE}/api/resource/Error Log/{urllib.parse.quote(err['name'])}").json().get('data', {})
            print(f" - {err_doc.get('creation')} | Method: {err_doc.get('method')} | Error: {str(err_doc.get('error'))[:100]}...")
except Exception as e:
    log_test("System Health", "Error Log Audit", False, str(e))

print("\n================================================================================")
print(f"AUDIT FINISHED: {results['tests_run']} Tests | PASSED: {results['passed']} | FAILED: {results['failed']} | WARNINGS: {results['warnings']}")
print("================================================================================")

# Save JSON audit output
with open("tools/integrity_check_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
