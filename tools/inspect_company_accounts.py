import requests
import json

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f'{BASE_URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

def get_company_details(company_name):
    c = session.get(f'{BASE_URL}/api/resource/Company/{requests.utils.quote(company_name)}').json().get('data', {})
    print(f"\n--- Company: {company_name} ---")
    print(f"Abbr: {c.get('abbr')}")
    print(f"Default Receivable: {c.get('default_receivable_account')}")
    print(f"Default Payable: {c.get('default_payable_account')}")
    print(f"Default Cash: {c.get('default_cash_account')}")
    print(f"Default Bank: {c.get('default_bank_account')}")
    print(f"Cost Center: {c.get('cost_center')}")
    print(f"Default Income: {c.get('default_income_account')}")
    print(f"Default Expense: {c.get('default_expense_account')}")
    return c

c1 = get_company_details("Ultra MRF Warehouse Dau")
c2 = get_company_details("Ultra MRF Dau Main")
c3 = get_company_details("ULTRA MRF")
