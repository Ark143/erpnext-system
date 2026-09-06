import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'})

mc = session.get(f"{BASE_URL}/api/resource/Company/My%20Company").json().get('data', {})
print("My Company details:")
print(f" - default_currency: {mc.get('default_currency')}")
print(f" - default_receivable_account: {mc.get('default_receivable_account')}")
print(f" - default_payable_account: {mc.get('default_payable_account')}")

# Check Debtors - MC account currency
acc = session.get(f"{BASE_URL}/api/resource/Account/Debtors%20-%20MC").json().get('data', {})
print("\nAccount 'Debtors - MC':")
print(f" - account_currency: {acc.get('account_currency')}")
print(f" - company: {acc.get('company')}")
