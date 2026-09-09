import requests
import json
import shutil
import os
import urllib.parse

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
login_res = s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})
print("Logged into VPS:", login_res.status_code)

# 1. Update Website Settings
res_web = s.put(f"{VPS_BASE}/api/resource/Website Settings/Website Settings", json={
    "app_name": "AUTOMAN CAR CARE CENTER",
    "app_logo": "/files/automan_logo.png",
    "banner_image": "/files/automan_logo.png",
    "favicon": "/files/automan_favicon.png",
    "splash_image": "/files/automan_logo.png"
})
print("Website Settings update status:", res_web.status_code, res_web.text[:100])

# 2. Update Navbar Settings
res_nav = s.put(f"{VPS_BASE}/api/resource/Navbar Settings/Navbar Settings", json={
    "app_logo": "/files/automan_logo.png"
})
print("Navbar Settings update status:", res_nav.status_code, res_nav.text[:100])

# 3. Update Company Logos across all companies
companies_res = s.get(f"{VPS_BASE}/api/resource/Company?limit_page_length=100")
companies = companies_res.json().get("data", [])
for c in companies:
    c_name = c.get("name")
    quoted_name = urllib.parse.quote(c_name)
    res_c = s.put(f"{VPS_BASE}/api/resource/Company/{quoted_name}", json={
        "company_logo": "/files/automan_logo.png"
    })
    print(f"Company '{c_name}' logo updated:", res_c.status_code)

# 4. Check / Update Letter Heads
lh_html = """
<div style="text-align: center; padding: 12px 0; background-color: #000; border-radius: 6px; margin-bottom: 20px;">
    <img src="/files/automan_logo.png" alt="AUTOMAN CAR CARE CENTER" style="max-height: 65px; display: inline-block;">
</div>
"""

for lh_name in ["AUTOMAN", "Automan Car Care Center", "Company Letterhead"]:
    res_lh_get = s.get(f"{VPS_BASE}/api/resource/Letter Head/{urllib.parse.quote(lh_name)}")
    if res_lh_get.status_code == 200:
        res_up = s.put(f"{VPS_BASE}/api/resource/Letter Head/{urllib.parse.quote(lh_name)}", json={
            "content": lh_html,
            "disabled": 0
        })
        print(f"Updated Letter Head '{lh_name}':", res_up.status_code)
    else:
        res_cr = s.post(f"{VPS_BASE}/api/resource/Letter Head", json={
            "letter_head_name": lh_name,
            "content": lh_html,
            "is_default": 1 if lh_name == "AUTOMAN" else 0,
            "disabled": 0
        })
        print(f"Created Letter Head '{lh_name}':", res_cr.status_code)

# 5. Ensure AUTOMAN company exists and has full configuration
# Check if AUTOMAN company exists
res_auto_c = s.get(f"{VPS_BASE}/api/resource/Company/AUTOMAN")
if res_auto_c.status_code == 200:
    print("Company AUTOMAN already exists:", res_auto_c.json().get("data", {}).get("name"))
else:
    print("Checking if Automan Car Care Center exists...")
    res_autocare = s.get(f"{VPS_BASE}/api/resource/Company/Automan%20Car%20Care%20Center")
    if res_autocare.status_code == 200:
        print("Automan Car Care Center exists with abbr:", res_autocare.json().get("data", {}).get("abbr"))
    
    # Also check if we should create a dedicated company named 'AUTOMAN'
    # Let's check if AUTOMAN is desired as a company name
    try:
        res_create_automan = s.post(f"{VPS_BASE}/api/resource/Company", json={
            "company_name": "AUTOMAN",
            "abbr": "AUTO",
            "default_currency": "PHP",
            "country": "Philippines",
            "company_logo": "/files/automan_logo.png",
            "is_group": 0,
            "parent_company": "ULTRA MRF",
            "create_chart_of_accounts_based_on": "Existing Company",
            "existing_company": "ULTRA MRF"
        })
        print("Created Company AUTOMAN:", res_create_automan.status_code, res_create_automan.text[:100])
    except Exception as e:
        print("Error creating AUTOMAN company:", e)

# 6. Copy local files to codebase
for dest_dir in [
    r"c:\Users\josem\erpnext-system\frappe-bench\apps\erpnext\erpnext\public\images",
    r"c:\Users\josem\erpnext-system\frappe-bench\apps\frappe\frappe\public\images"
]:
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy(r"c:\Users\josem\erpnext-system\tools\automan_logo.png", os.path.join(dest_dir, "automan_logo.png"))
    shutil.copy(r"c:\Users\josem\erpnext-system\tools\automan_favicon.png", os.path.join(dest_dir, "automan_favicon.png"))
    shutil.copy(r"c:\Users\josem\erpnext-system\tools\automan_logo.png", os.path.join(dest_dir, "erpnext-logo.png"))
    shutil.copy(r"c:\Users\josem\erpnext-system\tools\automan_logo.png", os.path.join(dest_dir, "erpnext-logo-blue.png"))
    shutil.copy(r"c:\Users\josem\erpnext-system\tools\automan_logo.png", os.path.join(dest_dir, "ultra_mrf_logo.png"))
    shutil.copy(r"c:\Users\josem\erpnext-system\tools\automan_logo.png", os.path.join(dest_dir, "frappe-framework-logo.png"))
    shutil.copy(r"c:\Users\josem\erpnext-system\tools\automan_logo.png", os.path.join(dest_dir, "frappe-logo.png"))
print("Copied all logos into local codebase public directories!")
