import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

create_script = """
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
    
    company = d.get('company') or frappe.defaults.get_user_default('Company') or 'ULTRA MRF'
    if company in ['All Branches', 'All', 'null', 'undefined']:
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
    # Direct match or alias
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

    # 3. Ensure POS Opening Entry for this cashier shift
    user = frappe.session.user
    existing_open = frappe.db.get_value('POS Opening Entry', {'user': user, 'company': company, 'pos_profile': profile_name, 'status': 'Open', 'docstatus': 1}, 'name')
    if not existing_open:
        other_open = frappe.get_all('POS Opening Entry', filters={'user': user, 'status': 'Open', 'docstatus': 1}, fields=['name'])
        for o in other_open:
            frappe.db.set_value('POS Opening Entry', o.name, 'status', 'Closed', update_modified=False)
        
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

    # 4. Prepare items
    items = []
    for it in (d.get('items') or []):
        items.append({
            'item_code': it.get('item_code'),
            'qty': float(it.get('qty') or 1),
            'rate': float(it.get('rate') or 0),
            'discount_amount': float(it.get('discount_amount') or 0),
            'uom': it.get('uom')
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

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote('VM POS Create Invoice'),
    data=json.dumps({'script': create_script, 'allow_guest': 1}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)
res = opener.open(req)
print("Updated VM POS Create Invoice Server Script:", res.status)
