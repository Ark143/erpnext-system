import requests

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

# Check all accounts of My Company
accs = s.get(f"{VPS_BASE}/api/resource/Account?filters=[[\"company\",\"=\",\"My Company\"]]&fields=[\"name\",\"account_currency\",\"account_type\"]&limit_page_length=200").json().get("data", [])
for a in accs:
    if a.get("account_currency") != "PHP":
        print(f"Fixing account {a.get('name')}: was {a.get('account_currency')}")
        s.put(f"{VPS_BASE}/api/resource/Account/{requests.utils.quote(a.get('name'))}", json={"account_currency": "PHP"})

res = s.put(f"{VPS_BASE}/api/resource/Company/My%20Company", json={"company_logo": "/files/automan_logo.png"})
print("Company update status:", res.status_code)
mc_after = s.get(f"{VPS_BASE}/api/resource/Company/My%20Company").json().get("data", {})
print("My Company Logo after update:", mc_after.get("company_logo"))
