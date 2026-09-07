import requests

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

res = session.get(f"{BASE_URL}/api/resource/Stock%20Ledger%20Entry?limit_page_length=2&fields=[\"item_code\",\"warehouse\",\"company\",\"posting_date\",\"posting_time\",\"voucher_type\",\"voucher_no\",\"actual_qty\",\"qty_after_transaction\",\"incoming_rate\",\"valuation_rate\",\"stock_value\",\"stock_value_difference\"]")
print("SLE fields sample:", res.json().get("data", []))

item_count_res = session.get(f"{BASE_URL}/api/resource/Item?limit_page_length=1&fields=[\"name\"]")
print("Item query headers:", item_count_res.headers)
