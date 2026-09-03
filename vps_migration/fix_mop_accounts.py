"""
Fix Mode of Payment accounts for missing companies.
All companies already have BDO bank accounts.
"""
import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# Company -> BDO bank account mapping (found from the bank account query)
company_bdo_accounts = {
    'Automan Car Care Center': 'BDO - AUTOMAN',
    'Ultra MRF Mexico Warehouse': 'BDO - MEXWH',
    'San Fernando Warehouse': 'BDO - SFWH',
    'The Wheelhub': 'BDO - WHUB',
    'Wheel Core': 'BDO - WCORE',
    'Ultra MRF Telebastagan 2': 'BDO - UMTEL2',
    'Ultra MRF Telebastagan': 'BDO - UMTEL',
    'Ultra MRF San Fernando': 'BDO - UMSF',
    'Ultra MRF Warehouse Dau': 'BDO - UMDW',
    'Ultra MRF Dau Main': 'BDO - UMDM',
    'Ultra MRF Dau Annex': 'BDO - UMDA',
    'ULTRA MRF': 'BDO - UM',
}

# Company -> Cash account mapping (for non-bank MoPs)
company_cash_accounts = {
    'Ultra MRF Mexico Warehouse': 'Cash - MEXWH',
    'Ultra MRF Warehouse Dau': 'Cash - UMDW',
    'Ultra MRF San Fernando': 'Cash - UMSF',
    'Ultra MRF Telebastagan': 'Cash - UMTEL',
    'Ultra MRF Telebastagan 2': 'Cash - UMTEL2',
    'My Company': 'Cash - MC',
    'Wheel Core': 'Cash - WCORE',
    'The Wheelhub': 'Cash - WHUB',
    'Automan Car Care Center': 'Cash - AUTOMAN',
    'San Fernando Warehouse': 'Cash - SFWH',
    'Ultra MRF Dau Main': 'Cash - UMDM',
    'Ultra MRF Dau Annex': 'Cash - UMDA',
    'ULTRA MRF': 'Cash - UM',
}

# Define which account to use for each MoP type
# Bank-type MoPs use BDO accounts; Cash/digital payment MoPs use Cash accounts
mop_account_map = {
    'BDO': company_bdo_accounts,   # Bank type -> BDO accounts
    'Bank Transfer': company_bdo_accounts,  # Bank type -> BDO accounts
    'GCash': company_cash_accounts,  # Cash/e-wallet -> Cash accounts
    'Maya': company_cash_accounts,   # Cash/e-wallet -> Cash accounts
    'Card': company_cash_accounts,   # Card -> Cash accounts (or can be BDO)
    'Credit Card': company_cash_accounts,  # Card -> Cash accounts
}

for mop_name, account_map in mop_account_map.items():
    print(f'Processing MoP: {mop_name}')
    r = opener.open('http://38.247.138.224:10017/api/resource/Mode%20of%20Payment/' + urllib.parse.quote(mop_name))
    mop = json.loads(r.read().decode())['data']
    
    # Get existing companies
    existing = {a['company']: a for a in mop.get('accounts', [])}
    existing_companies = set(existing.keys())
    
    # Add missing companies
    updated_accounts = list(mop.get('accounts', []))
    added = []
    for company, account in account_map.items():
        if company not in existing_companies:
            updated_accounts.append({
                'doctype': 'Mode of Payment Account',
                'company': company,
                'default_account': account,
            })
            added.append(company)
    
    if added:
        # Update the MoP with all accounts
        req = urllib.request.Request(
            'http://38.247.138.224:10017/api/resource/Mode%20of%20Payment/' + urllib.parse.quote(mop_name),
            data=json.dumps({'accounts': updated_accounts}).encode(),
            headers={'Content-Type': 'application/json'},
            method='PUT'
        )
        try:
            r_put = opener.open(req)
            r_data = json.loads(r_put.read().decode())
            print(f'  Added {len(added)} companies to {mop_name}: {added}')
        except urllib.error.HTTPError as e:
            print(f'  ERROR updating {mop_name}:', e.code, e.read().decode()[:300])
    else:
        print(f'  {mop_name}: No missing companies, skipping.')

# Trigger clear cache via Print Settings (known to invoke frappe.clear_cache())
print('\nClearing cache...')
r_ps = opener.open('http://38.247.138.224:10017/api/resource/Print%20Settings/Print%20Settings')
ps_data = json.loads(r_ps.read().decode())['data']
req_ps = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Print%20Settings/Print%20Settings',
    data=json.dumps({'pdf_page_size': ps_data.get('pdf_page_size', 'A4')}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)
opener.open(req_ps)
print('Cache cleared.')
print('\nAll done!')
