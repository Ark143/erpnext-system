import requests, json

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=15)

html_path = r"c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\www\consolidated_financials.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Deploy a 1-line update script
ss_updater = {
    "doctype": "Server Script",
    "name": "VM Webpage Quick Update",
    "script_type": "API",
    "api_method": "vm_update_webpage_html",
    "allow_guest": 0,
    "disabled": 0,
    "script": """
html = frappe.form_dict.get("html")
if html:
    frappe.db.set_value("Web Page", "consolidated-multi-company-financials-inventory-audit", "main_section_html", html)
    frappe.db.commit()
    frappe.response["message"] = "Updated successfully"
else:
    frappe.response["message"] = "No HTML provided"
"""
}

# Create/update server script
chk = session.get(f"{BASE_URL}/api/resource/Server%20Script/VM%20Webpage%20Quick%20Update")
if chk.status_code == 200:
    session.put(f"{BASE_URL}/api/resource/Server%20Script/VM%20Webpage%20Quick%20Update", json=ss_updater)
else:
    session.post(f"{BASE_URL}/api/resource/Server%20Script", json=ss_updater)

# Call method
res = session.post(f"{BASE_URL}/api/method/vm_update_webpage_html", data={"html": html_content}, timeout=30)
print("Update response:", res.status_code, res.text)

# Verify
verify = session.get(f"{BASE_URL}/consolidated-financials", timeout=15)
print("Route status:", verify.status_code)
if "company-popover" in verify.text:
    print("[VERIFIED SUCCESS] Latest HTML with company filter and stock modal is active!")
