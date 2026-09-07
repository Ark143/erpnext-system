import requests, json

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
login_res = session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=20)
print("Logged in:", login_res.status_code)

html_path = r"c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\www\consolidated_financials.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

doc_name = "consolidated-multi-company-financials-inventory-audit"
res = session.put(f"{BASE_URL}/api/resource/Web%20Page/{doc_name}", json={"main_section_html": html_content}, timeout=30)
print(f"Updated Web Page: {res.status_code}")

verify_res = session.get(f"{BASE_URL}/consolidated-financials", timeout=20)
print("Route GET status:", verify_res.status_code)
if "company-popover" in verify_res.text:
    print("[VERIFIED] Company filter and stock modal HTML is live!")
