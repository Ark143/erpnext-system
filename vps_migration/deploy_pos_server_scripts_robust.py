import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# -------------------------------------------------------------
# 1. VM POS Create Invoice Server Script
# -------------------------------------------------------------
create_invoice_code = """
def vm_pos_create_invoice():
    d = frappe.form_dict.get('data') or frappe.form_dict
    if isinstance(d, str):
        d = json.loads(d)
    
    cust = d.get('customer')
    veh = d.get('vehicle')
    plate = ''
    if veh and frappe.db.exists('Customer Vehicle', veh):
        veh_row = frappe.db.get_value('Customer Vehicle', veh, ['customer', 'plate_no'], as_dict=True)
        if veh_row:
            if veh_row.get('customer'):
                cust = veh_row['customer']
            plate = veh_row.get('plate_no') or ''
    
    if not cust:
        cust = frappe.db.get_value('Customer', {}, 'name')
    
    company = d.get('company') or frappe.defaults.get_user_default('Company') or 'ULTRA MRF'
    if company in ['All Branches', 'All', 'null', 'undefined', '']:
        company = 'ULTRA MRF'
    
    # 1. Resolve or create POS Profile
    profile_name = frappe.db.get_value('POS Profile', {'company': company, 'disabled': 0}, 'name') or frappe.db.get_value('POS Profile', {'company': company}, 'name')
    if not profile_name:
        default_warehouse = (
            frappe.db.get_value('Company', company, 'default_fg_warehouse')
            or frappe.db.get_value('Warehouse', {'company': company, 'is_group': 0}, 'name')
        )
        income_account = frappe.db.get_value('Company', company, 'default_income_account')
        cost_center = frappe.db.get_value('Company', company, 'cost_center') or frappe.db.get_value('Cost Center', {'company': company, 'is_group': 0}, 'name')
        profile_name = f'Vehicle POS - {company}'
        if not frappe.db.exists('POS Profile', profile_name):
            prof_doc = frappe.get_doc({
                'doctype': 'POS Profile',
                'name': profile_name,
                'pos_profile_name': profile_name,
                'company': company,
                'warehouse': default_warehouse,
                'currency': frappe.db.get_value('Company', company, 'default_currency') or 'PHP',
                'income_account': income_account,
                'cost_center': cost_center,
                'payments': [{'default': 1, 'mode_of_payment': 'Cash'}],
                'write_off_account': income_account,
                'write_off_cost_center': cost_center
            })
            prof_doc.insert(ignore_permissions=True)

    # 2. Resolve Mode of Payment
    method = (d.get('payment_method') or 'Cash').strip()
    mop_map = {
        'Cash': 'Cash',
        'Card': 'Card' if frappe.db.exists('Mode of Payment', 'Card') else 'Credit Card',
        'Credit Card': 'Credit Card',
        'Debit Card': 'Credit Card',
        'GCash': 'GCash' if frappe.db.exists('Mode of Payment', 'GCash') else 'Cash',
        'Maya': 'Maya' if frappe.db.exists('Mode of Payment', 'Maya') else 'Cash',
        'BDO': 'BDO' if frappe.db.exists('Mode of Payment', 'BDO') else 'Wire Transfer',
        'Bank Transfer': 'Bank Transfer' if frappe.db.exists('Mode of Payment', 'Bank Transfer') else 'Wire Transfer',
        'Wire Transfer': 'Wire Transfer',
        'Check': 'Check',
        'Cheque': 'Check'
    }
    mop = mop_map.get(method, method)
    if not frappe.db.exists('Mode of Payment', mop):
        mop = 'Cash'

    # Ensure this mode of payment is present in the POS Profile
    prof_doc = frappe.get_doc('POS Profile', profile_name)
    existing_mops = [p.mode_of_payment for p in prof_doc.payments]
    if mop not in existing_mops:
        prof_doc.append('payments', {
            'mode_of_payment': mop,
            'default': 0,
            'allow_in_returns': 1
        })
        prof_doc.save(ignore_permissions=True)
        frappe.db.commit()

    # 3. Clean up stale / outdated POS Opening Entries and ensure valid entry for today
    today_str = frappe.utils.today()
    user = frappe.session.user
    
    # Close any open entries for this profile that are outdated (not today)
    all_open_for_prof = frappe.get_all(
        'POS Opening Entry',
        filters={'pos_profile': profile_name, 'status': 'Open', 'docstatus': 1},
        fields=['name', 'period_start_date', 'posting_date', 'user']
    )
    
    valid_open_entry = None
    for oe in all_open_for_prof:
        start_d = frappe.utils.get_date_str(oe.period_start_date or oe.posting_date)
        if start_d != today_str:
            frappe.db.set_value('POS Opening Entry', oe.name, 'status', 'Closed', update_modified=False)
        else:
            if not valid_open_entry:
                valid_open_entry = oe.name
            else:
                # If duplicate open entries for same profile on same day, close excess
                frappe.db.set_value('POS Opening Entry', oe.name, 'status', 'Closed', update_modified=False)
    
    # Close any outdated open entries for this user in other profiles
    user_other_open = frappe.get_all(
        'POS Opening Entry',
        filters={'user': user, 'status': 'Open', 'docstatus': 1},
        fields=['name', 'pos_profile', 'period_start_date', 'posting_date']
    )
    for uo in user_other_open:
        start_d = frappe.utils.get_date_str(uo.period_start_date or uo.posting_date)
        if start_d != today_str or uo.pos_profile != profile_name:
            frappe.db.set_value('POS Opening Entry', uo.name, 'status', 'Closed', update_modified=False)

    frappe.db.commit()

    # If no valid open entry exists for today, create one
    if not valid_open_entry:
        entry = frappe.get_doc({
            'doctype': 'POS Opening Entry',
            'company': company,
            'pos_profile': profile_name,
            'user': user,
            'posting_date': frappe.utils.nowdate(),
            'period_start_date': frappe.utils.now_datetime(),
            'balance_details': [{'mode_of_payment': 'Cash', 'opening_amount': 0}]
        })
        entry.insert(ignore_permissions=True)
        entry.submit()
        frappe.db.commit()
        valid_open_entry = entry.name

    # 4. Prepare items
    items = []
    for it in (d.get('items') or []):
        items.append({
            'item_code': it.get('item_code'),
            'qty': float(it.get('qty') or 1),
            'rate': float(it.get('rate') or 0),
            'discount_amount': float(it.get('discount_amount') or 0),
            'uom': it.get('uom') or 'Nos'
        })

    # 5. Create and Submit POS Invoice
    paid_amount = float(d.get('paid_amount') or 0)
    inv = frappe.get_doc({
        'doctype': 'POS Invoice',
        'naming_series': 'ACC-PSINV-.YYYY.-',
        'company': company,
        'customer': cust,
        'posting_date': frappe.utils.nowdate(),
        'pos_profile': profile_name,
        'items': items,
        'payments': [{
            'mode_of_payment': mop,
            'amount': paid_amount
        }],
        'custom_customer_vehicle': veh or '',
        'custom_plate_no': plate,
        'remarks': (d.get('remarks') or d.get('notes') or '').strip()
    })
    inv.insert(ignore_permissions=True)
    inv.submit()
    frappe.db.commit()

    frappe.response['message'] = {
        'name': inv.name,
        'pos_invoice': inv.name,
        'grand_total': inv.grand_total,
        'paid_amount': inv.paid_amount,
        'payment_method': mop,
        'status': inv.status
    }

vm_pos_create_invoice()
"""

# -------------------------------------------------------------
# 2. VM POS Get Shift Server Script
# -------------------------------------------------------------
get_shift_code = """
def vm_pos_get_shift():
    user = frappe.session.user
    company = frappe.form_dict.get('company') or frappe.defaults.get_user_default('Company')
    today_str = frappe.utils.today()
    
    # Find existing open POS Opening Entry for this cashier
    filters = {'user': user, 'status': 'Open', 'docstatus': 1}
    if company and company not in ['All Branches', 'All', 'null', 'undefined']:
        filters['company'] = company
    
    existing = frappe.db.get_value(
        'POS Opening Entry',
        filters,
        ['name', 'pos_profile', 'company', 'posting_date', 'period_start_date',
         'set_posting_date', 'pos_closing_entry'],
        as_dict=True
    )
    
    # Check if existing shift is outdated (not from today)
    if existing:
        start_d = frappe.utils.get_date_str(existing.get('period_start_date') or existing.get('posting_date'))
        if start_d != today_str:
            frappe.db.set_value('POS Opening Entry', existing['name'], 'status', 'Closed', update_modified=False)
            frappe.db.commit()
            existing = None

    if existing:
        # Get cash opening balance from balance_details
        balance = frappe.db.get_value(
            'POS Opening Entry Detail',
            {'parent': existing['name']},
            ['mode_of_payment', 'opening_amount'],
            as_dict=True
        )
        existing['opening_amount'] = balance['opening_amount'] if balance else 0
        existing['mode_of_payment'] = balance['mode_of_payment'] if balance else 'Cash'
        frappe.response['message'] = {'has_open_shift': True, 'shift': existing}
    else:
        # Return available POS profiles and modes of payment for new shift
        p_filters = {'disabled': 0}
        if company and company not in ['All Branches', 'All', 'null', 'undefined']:
            p_filters['company'] = company
        profiles = frappe.get_all('POS Profile', 
            filters=p_filters,
            fields=['name', 'company'],
            limit=20
        )
        mops = frappe.get_all('Mode of Payment',
            filters={'enabled': 1},
            fields=['name', 'type'],
            order_by='type asc',
            limit=20
        )
        frappe.response['message'] = {
            'has_open_shift': False,
            'shift': None,
            'profiles': profiles,
            'modes_of_payment': mops,
            'company': company
        }

vm_pos_get_shift()
"""

# -------------------------------------------------------------
# 3. VM POS Open Shift Server Script
# -------------------------------------------------------------
open_shift_code = """
def vm_pos_open_shift():
    user = frappe.session.user
    d = frappe.form_dict.get('data') or frappe.form_dict
    if isinstance(d, str):
        d = json.loads(d)
    
    company = d.get('company') or frappe.defaults.get_user_default('Company') or 'ULTRA MRF'
    if company in ['All Branches', 'All', 'null', 'undefined', '']:
        company = 'ULTRA MRF'
        
    opening_amount = float(d.get('opening_amount') or 0)
    mop = d.get('mode_of_payment') or 'Cash'
    
    # Validate mode of payment exists
    if not frappe.db.exists('Mode of Payment', mop):
        mop = frappe.db.get_value('Mode of Payment', {'type': 'Cash'}, 'name') or 'Cash'
    
    # Get or auto-create POS Profile
    profile_name = d.get('pos_profile')
    if not profile_name:
        profile_name = frappe.db.get_value('POS Profile', {'company': company, 'disabled': 0}, 'name')
    if not profile_name:
        default_warehouse = (
            frappe.db.get_value('Company', company, 'default_fg_warehouse')
            or frappe.db.get_value('Warehouse', {'company': company, 'is_group': 0}, 'name')
        )
        income_account = frappe.db.get_value('Company', company, 'default_income_account')
        cost_center = (
            frappe.db.get_value('Company', company, 'cost_center')
            or frappe.db.get_value('Cost Center', {'company': company, 'is_group': 0}, 'name')
        )
        profile_name = f'Vehicle POS - {company}'
        if not frappe.db.exists('POS Profile', profile_name):
            prof_doc = frappe.get_doc({
                'doctype': 'POS Profile',
                'name': profile_name,
                'pos_profile_name': profile_name,
                'company': company,
                'warehouse': default_warehouse,
                'currency': frappe.db.get_value('Company', company, 'default_currency') or 'PHP',
                'income_account': income_account,
                'cost_center': cost_center,
                'payments': [{'default': 1, 'mode_of_payment': 'Cash'}],
                'write_off_account': income_account,
                'write_off_cost_center': cost_center
            })
            prof_doc.insert(ignore_permissions=True)
            frappe.db.commit()

    # Close any existing open entries for this user or profile
    other_open = frappe.get_all('POS Opening Entry', filters={'status': 'Open', 'docstatus': 1}, fields=['name', 'user', 'pos_profile'])
    for o in other_open:
        if o.user == user or o.pos_profile == profile_name:
            frappe.db.set_value('POS Opening Entry', o.name, 'status', 'Closed', update_modified=False)
    frappe.db.commit()

    # Create new POS Opening Entry
    entry = frappe.get_doc({
        'doctype': 'POS Opening Entry',
        'company': company,
        'pos_profile': profile_name,
        'user': user,
        'posting_date': frappe.utils.nowdate(),
        'period_start_date': frappe.utils.now_datetime(),
        'balance_details': [{
            'mode_of_payment': mop,
            'opening_amount': opening_amount
        }]
    })
    entry.insert(ignore_permissions=True)
    entry.submit()
    frappe.db.commit()

    frappe.response['message'] = {
        'name': entry.name,
        'pos_profile': profile_name,
        'company': company,
        'posting_date': str(entry.posting_date),
        'period_start_date': str(entry.period_start_date),
        'status': entry.status,
        'opening_amount': opening_amount,
        'mode_of_payment': mop
    }

vm_pos_open_shift()
"""

# Update all Server Scripts
scripts_to_update = [
    ("VM POS Create Invoice", "vm_pos_create_invoice", create_invoice_code),
    ("VM POS Get Shift", "vm_pos_get_shift", get_shift_code),
    ("VM POS Open Shift", "vm_pos_open_shift", open_shift_code)
]

for name, api, script_text in scripts_to_update:
    payload = {
        "name": name,
        "script_type": "API",
        "api_method": api,
        "disabled": 0,
        "allow_guest": 1,
        "script": script_text
    }
    check = s.get(f'{URL}/api/resource/Server%20Script/{name}')
    if check.status_code == 200:
        res = s.put(f'{URL}/api/resource/Server%20Script/{name}', json=payload)
    else:
        res = s.post(f'{URL}/api/resource/Server%20Script', json=payload)
    print(f"Updated {name}: HTTP {res.status_code}")

print("\n--- Testing vm_pos_create_invoice after update ---")
test_cust = s.get(f'{URL}/api/resource/Customer?limit=1').json().get('data', [])[0]['name']
test_item = s.get(f'{URL}/api/resource/Item?limit=1&filters=[["is_sales_item","=",1]]').json().get('data', [])[0]['name']
res = s.post(f'{URL}/api/method/vm_pos_create_invoice', json={
    'data': {
        'company': 'ULTRA MRF',
        'customer': test_cust,
        'payment_method': 'Cash',
        'paid_amount': 250,
        'items': [{'item_code': test_item, 'qty': 1, 'rate': 250, 'uom': 'Nos'}]
    }
})
print("vm_pos_create_invoice result:", json.dumps(res.json(), indent=2))
