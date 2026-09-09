import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

# 1. Check existing non-stock service items
items_res = s.get(f"{VPS_BASE}/api/resource/Item?filters=[[\"is_stock_item\",\"=\",0]]&fields=[\"name\",\"item_name\",\"item_group\",\"standard_rate\"]&limit_page_length=50")
items = items_res.json().get("data", [])
print(f"Service Items count: {len(items)}")
for itm in items[:15]:
    print(f"- {itm.get('name')} | {itm.get('item_name')} | Group: {itm.get('item_group')} | Rate: {itm.get('standard_rate')}")

# 2. Check Customer list
cust_res = s.get(f"{VPS_BASE}/api/resource/Customer?limit_page_length=50&fields=[\"name\",\"customer_name\",\"customer_group\"]")
customers = cust_res.json().get("data", [])
print(f"\nCustomers count: {len(customers)}")
for c in customers[:10]:
    print(f"- {c.get('name')} | {c.get('customer_name')}")

# 3. Check Customer Vehicles if any
veh_res = s.get(f"{VPS_BASE}/api/resource/Customer Vehicle?limit_page_length=50&fields=[\"name\",\"plate_number\",\"make\",\"model\",\"customer\"]")
vehicles = veh_res.json().get("data", [])
print(f"\nCustomer Vehicles count: {len(vehicles)}")
for v in vehicles[:10]:
    print(f"- {v.get('name')} | Plate: {v.get('plate_number')} | {v.get('make')} {v.get('model')} | Customer: {v.get('customer')}")

# 4. Check Automan Company accounts
c_doc = s.get(f"{VPS_BASE}/api/resource/Company/Automan%20Car%20Care%20Center").json().get("data", {})
print("\nAutoman Company Setup:")
print("Income Account:", c_doc.get("default_income_account"))
print("Receivable Account:", c_doc.get("default_receivable_account"))
print("Cash Account:", c_doc.get("default_cash_account"))
print("Cost Center:", c_doc.get("cost_center"))
