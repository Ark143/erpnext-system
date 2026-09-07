import requests, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
login_res = session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)
login_res.raise_for_status()
print("[OK] Logged in to VPS as Administrator")

html_path = r"c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\www\consolidated_financials.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

web_page_data = {
    "main_section_html": html_content,
    "published": 1,
    "full_width": 1,
    "show_title": 0,
    "show_sidebar": 0
}

doc_name = "consolidated-multi-company-financials-inventory-audit"
res = session.put(f"{BASE_URL}/api/resource/Web%20Page/{doc_name}", json=web_page_data)
print(f"Updated Web Page '{doc_name}': {res.status_code}")

verify_res = session.get(f"{BASE_URL}/consolidated-financials")
print(f"Testing route GET /consolidated-financials: Status {verify_res.status_code}")
if "tab-nav-balance_sheet" in verify_res.text:
    print("[VERIFIED] Latest HTML is active on /consolidated-financials!")
