import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

create_invoice_code = """
def vm_pos_create_invoice():
    d = frappe.form_dict.get('data') or frappe.form_dict
    if isinstance(d, str):
        d = json.loads(d)
    
    company = d.get('company') or frappe.defaults.get_user_default('Company') or 'ULTRA MRF'
    if company in ['All Branches', 'All', 'null', 'undefined', '', None]:
        company = 'ULTRA MRF'
    
    # 1. Resolve Customer and Vehicle
    cust = (d.get('customer') or '').strip()
    veh = (d.get('vehicle') or '').strip()
    plate = ''
    
    # If customer is formatted as "CODE — NAME", extract code
    if '—' in cust:
        cust = cust.split('—')[0].strip()
    elif ' - ' in cust:
        cust = cust.split(' - ')[0].strip()
        
    real_veh_doc = ''
    if veh:
        if frappe.db.exists('Customer Vehicle', veh):
            real_veh_doc = veh
            veh_row = frappe.db.get_value('Customer Vehicle', veh, ['customer', 'plate_no'], as_dict=True)
            if veh_row:
                if not cust and veh_row.get('customer'):
                    cust = veh_row['customer']
                plate = veh_row.get('plate_no') or veh
        else:
            # Check if veh is a plate number in DB
            match_veh = frappe.db.get_value('Customer Vehicle', {'plate_no': veh}, 'name')
            if match_veh:
                real_veh_doc = match_veh
                plate = veh
            else:
                # Store as plate text only, do not set link field to invalid ID
                plate = str(veh)
                real_veh_doc = ''

    # Validate or find customer
    if cust and not frappe.db.exists('Customer', cust):
        real_cust = frappe.db.get_value('Customer', {'customer_name': cust}, 'name') \
            or frappe.db.get_value('Customer', {'customer_name': ['like', f'%{cust}%']}, 'name')
        if real_cust:
            cust = real_cust
        else:
            # Auto-create customer with this name
            try:
                cg = frappe.db.get_value('Customer Group', {'is_group': 0}, 'name') or 'Individual'
                terr = frappe.db.get_value('Territory', {'is_group': 0}, 'name') or 'Philippines'
                c_doc = frappe.get_doc({
                    'doctype': 'Customer',
                    'customer_name': cust,
                    'customer_type': 'Individual',
                    'customer_group': cg,
                    'territory': terr
                })
                c_doc.insert(ignore_permissions=True)
                cust = c_doc.name
            except Exception:
                cust = ''
            
    if not cust or not frappe.db.exists('Customer', cust):
        # Fallback to default walk-in customer or first customer
        cust = frappe.db.get_value('Customer', {'customer_name': ['like', '%Cash%']}, 'name') \
            or frappe.db.get_value('Customer', {'customer_name': ['like', '%Walk%']}, 'name') \
            or frappe.db.get_value('Customer', {}, 'name')

    # 2. Resolve or create POS Profile
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

    # 3. Resolve Mode of Payment
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

    # 4. Clean up stale / outdated POS Opening Entries and ensure valid entry for today
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

    # 5. Prepare items with link resolution
    items = []
    default_sales_item = frappe.db.get_value('Item', {'is_sales_item': 1, 'disabled': 0}, 'name')
    
    for it in (d.get('items') or []):
        raw_code = (it.get('item_code') or it.get('code') or '').strip()
        clean_code = raw_code.rstrip('.').strip()
        
        # Check if item exists by exact code
        if frappe.db.exists('Item', raw_code):
            real_code = raw_code
        elif frappe.db.exists('Item', clean_code):
            real_code = clean_code
        else:
            # Search by name or item_name
            real_code = frappe.db.get_value('Item', {'item_name': clean_code}, 'name') \
                or frappe.db.get_value('Item', {'item_name': ['like', f'{clean_code[:12]}%']}, 'name') \
                or frappe.db.get_value('Item', {'name': ['like', f'{clean_code[:12]}%']}, 'name') \
                or default_sales_item
                
        uom = it.get('uom')
        if not uom or not frappe.db.exists('UOM', uom):
            uom = frappe.db.get_value('Item', real_code, 'stock_uom') or 'Nos'
            if not frappe.db.exists('UOM', uom):
                uom = frappe.db.get_value('UOM', {}, 'name')
                
        items.append({
            'item_code': real_code,
            'qty': float(it.get('qty') or 1),
            'rate': float(it.get('rate') or 0),
            'discount_amount': float(it.get('discount_amount') or 0),
            'uom': uom
        })

    # 6. Create and Submit POS Invoice
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
        'custom_customer_vehicle': real_veh_doc,
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

payload = {
    "name": "VM POS Create Invoice",
    "script_type": "API",
    "api_method": "vm_pos_create_invoice",
    "disabled": 0,
    "allow_guest": 1,
    "script": create_invoice_code
}

res = s.put(f'{URL}/api/resource/Server%20Script/VM%20POS%20Create%20Invoice', json=payload)
print("Updated VM POS Create Invoice Server Script:", res.status_code)
