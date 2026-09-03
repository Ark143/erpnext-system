import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

script_code = """
def setup_payment_methods():
    companies = [
        {'name': 'ULTRA MRF', 'abbr': 'UM'},
        {'name': 'Ultra MRF Dau Main', 'abbr': 'UMDM'},
        {'name': 'Ultra MRF Dau Annex', 'abbr': 'UMDA'}
    ]
    
    # 1. Create Bank Ledger Accounts for each company
    bank_accounts = {}
    for c in companies:
        co_name = c['name']
        abbr = c['abbr']
        parent_bank = f'Bank Accounts - {abbr}'
        bdo_acc_name = f'BDO - {abbr}'
        
        if not frappe.db.exists('Account', bdo_acc_name):
            try:
                acc = frappe.get_doc({
                    'doctype': 'Account',
                    'account_name': 'BDO',
                    'company': co_name,
                    'parent_account': parent_bank,
                    'account_type': 'Bank',
                    'is_group': 0,
                    'currency': 'PHP'
                })
                acc.insert(ignore_permissions=True)
                frappe.db.commit()
            except Exception as e:
                frappe.log_error(f"Error creating account {bdo_acc_name}: {e}")
        
        bank_accounts[co_name] = bdo_acc_name if frappe.db.exists('Account', bdo_acc_name) else f'Cash - {abbr}'

    # 2. Define desired Modes of Payment
    modes = ['Cash', 'Credit Card', 'Card', 'GCash', 'Maya', 'BDO', 'Bank Transfer', 'Wire Transfer']
    
    for m in modes:
        if not frappe.db.exists('Mode of Payment', m):
            m_type = 'Cash' if m == 'Cash' else 'Bank'
            doc = frappe.get_doc({
                'doctype': 'Mode of Payment',
                'mode_of_payment': m,
                'type': m_type,
                'enabled': 1
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
        
        m_doc = frappe.get_doc('Mode of Payment', m)
        existing_companies = [a.company for a in m_doc.accounts]
        
        for c in companies:
            co_name = c['name']
            abbr = c['abbr']
            if co_name not in existing_companies:
                target_acc = f'Cash - {abbr}' if (m_doc.type == 'Cash' or m == 'Cash') else bank_accounts.get(co_name, f'Cash - {abbr}')
                m_doc.append('accounts', {
                    'company': co_name,
                    'default_account': target_acc
                })
        m_doc.save(ignore_permissions=True)
        frappe.db.commit()

    # 3. Update all POS Profiles to include all Modes of Payment
    pos_profiles = frappe.get_all('POS Profile', fields=['name', 'company'])
    for prof in pos_profiles:
        p_doc = frappe.get_doc('POS Profile', prof['name'])
        existing_mops = [p.mode_of_payment for p in p_doc.payments]
        
        for m in ['Cash', 'Card', 'Credit Card', 'GCash', 'Maya', 'BDO', 'Bank Transfer']:
            if frappe.db.exists('Mode of Payment', m) and m not in existing_mops:
                p_doc.append('payments', {
                    'mode_of_payment': m,
                    'default': 1 if m == 'Cash' else 0,
                    'allow_in_returns': 1
                })
        p_doc.save(ignore_permissions=True)
        frappe.db.commit()

    frappe.response['message'] = {
        'status': 'success',
        'bank_accounts': bank_accounts,
        'modes_configured': modes,
        'profiles_updated': [p['name'] for p in pos_profiles]
    }

setup_payment_methods()
"""

# Upload to Probe API to execute
req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote('Probe API'),
    data=json.dumps({'script': script_code}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)
opener.open(req)

res = opener.open('http://38.247.138.224:10017/api/method/vm_probe_api')
print(res.read().decode())
