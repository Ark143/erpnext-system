import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

# Update My Company logo
s.put(f"{VPS_BASE}/api/resource/Company/My%20Company", json={"company_logo": "/files/automan_logo.png"})

# Check Automan warehouses
whs = s.get(f"{VPS_BASE}/api/resource/Warehouse?filters=[[\"company\",\"=\",\"Automan Car Care Center\"]]&fields=[\"name\",\"warehouse_name\",\"is_group\"]").json()
print("Automan Warehouses:", json.dumps(whs.get("data", []), indent=2))

# Check Automan Cost Center
ccs = s.get(f"{VPS_BASE}/api/resource/Cost Center?filters=[[\"company\",\"=\",\"Automan Car Care Center\"]]&fields=[\"name\",\"cost_center_name\"]").json()
print("Automan Cost Centers:", json.dumps(ccs.get("data", []), indent=2))

# Check Automan Accounts count
accs = s.get(f"{VPS_BASE}/api/resource/Account?filters=[[\"company\",\"=\",\"Automan Car Care Center\"]]&limit_page_length=200").json()
print("Automan Total Accounts:", len(accs.get("data", [])))

# Verify Company Details
c_auto = s.get(f"{VPS_BASE}/api/resource/Company/Automan%20Car%20Care%20Center").json().get("data", {})
print("Company Name:", c_auto.get("name"))
print("Abbr:", c_auto.get("abbr"))
print("Logo:", c_auto.get("company_logo"))
print("Default Cash:", c_auto.get("default_cash_account"))
print("Default Receivable:", c_auto.get("default_receivable_account"))
print("Default Payable:", c_auto.get("default_payable_account"))
print("Default Income:", c_auto.get("default_income_account"))
print("Default Expense:", c_auto.get("default_expense_account"))
print("Default Inventory:", c_auto.get("default_inventory_account"))
