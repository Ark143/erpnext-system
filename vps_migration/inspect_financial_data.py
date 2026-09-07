import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

def inspect_financials():
    # 1. Get companies
    res = session.get(f"{BASE_URL}/api/resource/Company?fields=[\"name\",\"abbr\",\"default_currency\",\"country\"]&limit_page_length=50")
    companies = res.json().get("data", [])
    print(f"Total Companies: {len(companies)}")
    for c in companies:
        print(f" - {c['name']} ({c['abbr']}) [{c.get('default_currency')}]")

    # 2. Check Accounts per root type
    res = session.get(f"{BASE_URL}/api/resource/Account?fields=[\"name\",\"company\",\"root_type\",\"report_type\",\"account_type\",\"parent_account\",\"is_group\"]&limit_page_length=50")
    accounts = res.json().get("data", [])
    print(f"\nTotal Accounts sampled: {len(accounts)}")
    root_types = set([a.get('root_type') for a in accounts if a.get('root_type')])
    print(f"Root types found: {root_types}")

    # 3. Check GL Entries sample
    res = session.get(f"{BASE_URL}/api/resource/GL Entry?fields=[\"company\",\"voucher_type\",\"account\",\"debit\",\"credit\",\"posting_date\"]&limit_page_length=10")
    gl_entries = res.json().get("data", [])
    print(f"\nSample GL Entries count: {len(gl_entries)}")
    for g in gl_entries[:5]:
        print(f" - {g}")

    # 4. Check Stock / Bin
    res = session.get(f"{BASE_URL}/api/resource/Bin?fields=[\"item_code\",\"warehouse\",\"actual_qty\",\"valuation_rate\",\"stock_value\"]&limit_page_length=5")
    bins = res.json().get("data", [])
    print(f"\nSample Bins: {len(bins)}")
    for b in bins:
        print(f" - {b}")

if __name__ == "__main__":
    inspect_financials()
