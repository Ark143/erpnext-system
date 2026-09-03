import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

setup_script = """
def vm_setup_company_pos_profiles():
    results = []
    companies = frappe.get_all('Company', filters={'is_group': 0}, fields=['name', 'default_currency', 'default_fg_warehouse', 'default_income_account', 'cost_center'], order_by='name asc')
    
    # Standard payment modes to configure in each POS profile
    payment_methods = ['Cash', 'Card', 'Credit Card', 'GCash', 'Maya', 'BDO', 'Bank Transfer']
    
    for c in companies:
        cname = c['name']
        
        # 1. Resolve Warehouse
        warehouse = c.get('default_fg_warehouse')
        if not warehouse:
            warehouse = frappe.db.get_value('Warehouse', {'company': cname, 'is_group': 0}, 'name')
        if not warehouse:
            # Create default warehouse if missing
            wh_doc = frappe.get_doc({
                'doctype': 'Warehouse',
                'warehouse_name': f'Stores - {cname}',
                'company': cname
            })
            wh_doc.insert(ignore_permissions=True)
            warehouse = wh_doc.name
            
        # 2. Resolve Income Account
        income_account = c.get('default_income_account')
        if not income_account:
            income_account = frappe.db.get_value('Account', {'company': cname, 'root_type': 'Income', 'is_group': 0}, 'name')
            
        # 3. Resolve Cost Center
        cost_center = c.get('cost_center')
        if not cost_center:
            cost_center = frappe.db.get_value('Cost Center', {'company': cname, 'is_group': 0}, 'name')
            
        # 4. Resolve Currency
        currency = c.get('default_currency') or 'PHP'
        
        # 5. Resolve Cash and Bank accounts for Mode of Payment
        cash_account = frappe.db.get_value('Account', {'company': cname, 'account_type': 'Cash', 'is_group': 0}, 'name')
        bank_account = frappe.db.get_value('Account', {'company': cname, 'account_type': 'Bank', 'is_group': 0}, 'name') or cash_account
        
        # Ensure Mode of Payment has company account configured
        mop_account_pairs = [
            ('Cash', cash_account),
            ('Card', bank_account),
            ('Credit Card', bank_account),
            ('GCash', bank_account),
            ('Maya', bank_account),
            ('BDO', bank_account),
            ('Bank Transfer', bank_account),
        ]
        
        for mop_name, acc in mop_account_pairs:
            if mop_name and acc and frappe.db.exists('Mode of Payment', mop_name):
                mop_doc = frappe.get_doc('Mode of Payment', mop_name)
                has_co = any(a.company == cname for a in mop_doc.accounts)
                if not has_co:
                    mop_doc.append('accounts', {'company': cname, 'default_account': acc})
                    mop_doc.save(ignore_permissions=True)
                else:
                    # Update if missing default_account
                    for a in mop_doc.accounts:
                        if a.company == cname and not a.default_account:
                            a.default_account = acc
                    mop_doc.save(ignore_permissions=True)
        
        # 6. Create or update POS Profile: "Vehicle POS - {cname}"
        profile_name = f'Vehicle POS - {cname}'
        
        if frappe.db.exists('POS Profile', profile_name):
            prof_doc = frappe.get_doc('POS Profile', profile_name)
            prof_doc.disabled = 0
            if warehouse: prof_doc.warehouse = warehouse
            if income_account: prof_doc.income_account = income_account
            if cost_center: prof_doc.cost_center = cost_center
            prof_doc.currency = currency
            prof_doc.applicable_for_users = [] # Open to all authorized users of company
            
            # Ensure payments list has all payment methods
            existing_mops = [p.mode_of_payment for p in prof_doc.payments]
            for idx, pm in enumerate(payment_methods):
                if pm not in existing_mops and frappe.db.exists('Mode of Payment', pm):
                    prof_doc.append('payments', {
                        'mode_of_payment': pm,
                        'default': 1 if pm == 'Cash' else 0
                    })
            prof_doc.save(ignore_permissions=True)
            status = 'updated'
        else:
            payments_rows = []
            for pm in payment_methods:
                if frappe.db.exists('Mode of Payment', pm):
                    payments_rows.append({
                        'mode_of_payment': pm,
                        'default': 1 if pm == 'Cash' else 0
                    })
            
            prof_doc = frappe.get_doc({
                'doctype': 'POS Profile',
                'name': profile_name,
                'pos_profile_name': profile_name,
                'company': cname,
                'warehouse': warehouse,
                'income_account': income_account,
                'cost_center': cost_center,
                'currency': currency,
                'write_off_account': income_account,
                'write_off_cost_center': cost_center,
                'applicable_for_users': [],
                'payments': payments_rows,
                'disabled': 0
            })
            prof_doc.insert(ignore_permissions=True)
            status = 'created'
            
        results.append({
            'company': cname,
            'pos_profile': profile_name,
            'status': status,
            'warehouse': warehouse,
            'payments_count': len(prof_doc.payments)
        })
        
    frappe.db.commit()
    frappe.response['message'] = {'success': True, 'count': len(results), 'profiles': results}

vm_setup_company_pos_profiles()
"""

# Deploy temporary Server Script to run setup
url = 'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Setup%20Company%20POS%20Profiles'
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
payload = json.dumps({
    'doctype': 'Server Script',
    'name': 'VM Setup Company POS Profiles',
    'script_type': 'API',
    'api_method': 'vm_setup_company_pos_profiles',
    'allow_guest': 0,
    'script': setup_script
}).encode()

# Upsert server script
try:
    req = urllib.request.Request(url, data=payload, headers=H, method='PUT')
    res = opener.open(req)
except urllib.error.HTTPError as e:
    if e.code == 404:
        url_post = 'http://38.247.138.224:10017/api/resource/Server%20Script'
        req = urllib.request.Request(url_post, data=payload, headers=H, method='POST')
        res = opener.open(req)
    else:
        raise

print('Server script deployed, executing setup...')

# Execute setup API
r_exec = opener.open('http://38.247.138.224:10017/api/method/vm_setup_company_pos_profiles')
output = json.loads(r_exec.read().decode())['message']
count = output['count']
print('Setup executed successfully for ' + str(count) + ' companies:')
for p in output['profiles']:
    co = p['company']
    prof = p['pos_profile']
    st = p['status']
    wh = p['warehouse']
    cnt = p['payments_count']
    print('  ✔ ' + co + ': ' + prof + ' (' + st + ') | wh=' + str(wh) + ' | ' + str(cnt) + ' payments')

# Cleanup the temporary setup Server Script
try:
    req_del = urllib.request.Request(url, headers=H, method='DELETE')
    opener.open(req_del)
    print('Cleaned up temporary server script.')
except Exception as e:
    print('Note on cleanup:', e)
