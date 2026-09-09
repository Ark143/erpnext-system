import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})
mc = s.get(f"{VPS_BASE}/api/resource/Company/My%20Company").json().get("data", {})
print("My Company Currency:", mc.get("default_currency"))
print("Default Cash Account:", mc.get("default_cash_account"))
cash_acc_name = mc.get("default_cash_account")
if cash_acc_name:
    acc = s.get(f"{VPS_BASE}/api/resource/Account/{requests.utils.quote(cash_acc_name)}").json().get("data", {})
    print("Cash Account Doc:", acc.get("name"), "Account Currency:", acc.get("account_currency"))
    # Update account currency if needed
    if acc.get("account_currency") != mc.get("default_currency"):
        s.put(f"{VPS_BASE}/api/resource/Account/{requests.utils.quote(cash_acc_name)}", json={"account_currency": mc.get("default_currency")})
    
# Update My Company logo
res = s.put(f"{VPS_BASE}/api/resource/Company/My%20Company", json={"company_logo": "/files/automan_logo.png"})
print("Update status:", res.status_code)
mc_after = s.get(f"{VPS_BASE}/api/resource/Company/My%20Company").json().get("data", {})
print("My Company Logo after update:", mc_after.get("company_logo"))
