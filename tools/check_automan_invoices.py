import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

sinvs = s.get(f"{VPS_BASE}/api/resource/Sales Invoice?filters=[[\"company\",\"=\",\"Automan Car Care Center\"]]&fields=[\"name\",\"grand_total\",\"customer\",\"status\",\"posting_date\"]&limit_page_length=100").json().get("data", [])
print(f"Total Automan Sales Invoices: {len(sinvs)}")

payments = s.get(f"{VPS_BASE}/api/resource/Payment Entry?filters=[[\"company\",\"=\",\"Automan Car Care Center\"]]&fields=[\"name\",\"paid_amount\",\"party\",\"status\"]&limit_page_length=100").json().get("data", [])
print(f"Total Automan Payment Entries: {len(payments)}")

total_amt = sum([float(i.get("grand_total") or 0) for i in sinvs])
print(f"Total Billed Revenue: PHP {total_amt:,.2f}")
