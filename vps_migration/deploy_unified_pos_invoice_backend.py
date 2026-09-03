import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# =========================================================================
# 1. SERVER SCRIPT: VM POS Create Invoice (Creates standard POS Invoice)
# =========================================================================
create_invoice_script = """
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
    
    company = d.get('company') or frappe.defaults.get_user_default('Company')
    
    # Resolve or create default POS Profile
    profile_name = frappe.db.get_value('POS Profile', {'company': company, 'disabled': 0}, 'name') or frappe.db.get_value('POS Profile', {'company': company}, 'name')
    if not profile_name:
        default_warehouse = (
            frappe.db.get_value('Company', company, 'default_fg_warehouse')
            or frappe.db.get_value('Company', company, 'default_in_transit_warehouse')
            or frappe.db.get_value('Warehouse', {'company': company, 'is_group': 0}, 'name')
        )
        income_account = frappe.db.get_value('Company', company, 'default_income_account')
        cost_center = frappe.db.get_value('Company', company, 'cost_center') or frappe.db.get_value('Cost Center', {'company': company, 'is_group': 0}, 'name')
        cash_mop = frappe.db.get_value('Mode of Payment', {'type': 'Cash'}, 'name') or 'Cash'
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
                'payments': [{'default': 1, 'mode_of_payment': cash_mop}],
                'write_off_account': income_account,
                'write_off_cost_center': cost_center
            })
            prof_doc.insert(ignore_permissions=True)
    
    # Ensure POS Opening Entry for this shift
    user = frappe.session.user
    existing_open = frappe.db.get_value('POS Opening Entry', {'user': user, 'company': company, 'pos_profile': profile_name, 'status': 'Open', 'docstatus': 1}, 'name')
    if not existing_open:
        other_open = frappe.get_all('POS Opening Entry', filters={'user': user, 'status': 'Open', 'docstatus': 1}, fields=['name'])
        for o in other_open:
            frappe.db.set_value('POS Opening Entry', o.name, 'status', 'Closed', update_modified=False)
        
        cash_mop = frappe.db.get_value('Mode of Payment', {'type': 'Cash'}, 'name') or 'Cash'
        entry = frappe.get_doc({
            'doctype': 'POS Opening Entry',
            'company': company,
            'pos_profile': profile_name,
            'user': user,
            'posting_date': frappe.utils.nowdate(),
            'period_start_date': frappe.utils.now_datetime(),
            'balance_details': [{'mode_of_payment': cash_mop, 'opening_amount': 0}]
        })
        entry.insert(ignore_permissions=True)
        entry.submit()
    
    # Map payment method
    method = d.get('payment_method') or 'Cash'
    mop_map = {
        'Cash': 'Cash',
        'Card': 'Credit Card',
        'Credit Card': 'Credit Card',
        'Debit Card': 'Credit Card',
        'GCash': 'Cash',
        'Maya': 'Cash',
        'BDO': 'Wire Transfer',
        'Bank Transfer': 'Wire Transfer',
        'Cheque': 'Bank Draft',
        'Check': 'Check'
    }
    mop = mop_map.get(method, 'Cash')
    if not frappe.db.exists('Mode of Payment', mop):
        mop = frappe.db.get_value('Mode of Payment', {'type': 'Cash'}, 'name') or 'Cash'
    
    # Prepare items
    items = []
    for it in (d.get('items') or []):
        items.append({
            'item_code': it.get('item_code'),
            'qty': float(it.get('qty') or 1),
            'rate': float(it.get('rate') or 0),
            'discount_amount': float(it.get('discount_amount') or 0),
            'uom': it.get('uom')
        })
    
    # Create & Submit standard ERPNext POS Invoice
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
            'amount': float(d.get('paid_amount') or 0)
        }],
        'custom_customer_vehicle': veh or '',
        'custom_plate_no': plate,
        'remarks': (d.get('remarks') or d.get('notes') or '').strip()
    })
    inv.insert(ignore_permissions=True)
    inv.submit()
    
    frappe.response['message'] = {
        'name': inv.name,
        'pos_invoice': inv.name,
        'grand_total': inv.grand_total,
        'paid_amount': inv.paid_amount,
        'status': inv.status
    }

vm_pos_create_invoice()
"""

# Save or Update VM POS Create Invoice
req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote('VM POS Create Invoice'),
    data=json.dumps({'script': create_invoice_script}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)
res = opener.open(req)
print("1. Updated VM POS Create Invoice Server Script:", res.status)

# =========================================================================
# 2. SERVER SCRIPT: VM POS History (Queries standard POS Invoice directly)
# =========================================================================
history_script = """
def vm_pos_history():
    user = frappe.session.user
    is_manager = (user == 'Administrator') or bool(frappe.db.get_value('Has Role', {'parent': user, 'role': ['in', ['System Manager', 'Accounts Manager']]}, 'name'))
    
    filters = [['docstatus', '<', 2]]
    
    company = frappe.form_dict.get('company')
    if not is_manager:
        cashier_company = frappe.db.get_value('Employee', {'user_id': user}, 'company') or frappe.db.get_value('Cashier Profile', user, 'company')
        if cashier_company:
            filters.append(['company', '=', cashier_company])
        else:
            filters.append(['owner', '=', user])
    elif company:
        filters.append(['company', '=', company])
    
    period = frappe.form_dict.get('period')
    from_date = frappe.form_dict.get('from_date')
    to_date = frappe.form_dict.get('to_date')
    today_str = frappe.utils.today()
    
    if period == 'today':
        filters.append(['posting_date', '=', today_str])
    elif period == 'month':
        first_day = str(today_str)[:8] + '01'
        filters.append(['posting_date', '>=', first_day])
        filters.append(['posting_date', '<=', today_str])
    elif from_date or to_date:
        if from_date:
            filters.append(['posting_date', '>=', from_date])
        if to_date:
            filters.append(['posting_date', '<=', to_date])
    
    search = frappe.form_dict.get('search')
    or_filters = None
    if search:
        like = f'%{search.strip()}%'
        or_filters = [
            ['name', 'like', like],
            ['customer_name', 'like', like],
            ['custom_plate_no', 'like', like],
            ['custom_customer_vehicle', 'like', like]
        ]
    
    rows = frappe.get_all(
        'POS Invoice',
        filters=filters,
        or_filters=or_filters,
        fields=['name', 'posting_date', 'customer_name', 'custom_customer_vehicle as vehicle',
                'custom_plate_no as plate_no', 'grand_total as total_amount', 'paid_amount',
                'company', 'creation', 'status', 'remarks', 'owner as cashier'],
        order_by='creation desc',
        limit_page_length=200
    )
    
    for r in rows:
        c = r.get('creation') or ''
        r['timestamp'] = str(c)[:19] if c else str(r.get('posting_date') or '')
        r['pos_invoice'] = r['name']
        mop = frappe.db.get_value('Sales Invoice Payment', {'parent': r['name']}, 'mode_of_payment')
        r['payment_method'] = mop or 'Cash'
        
    frappe.response['message'] = rows

vm_pos_history()
"""

req2 = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote('VM POS History'),
    data=json.dumps({'script': history_script}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)
res2 = opener.open(req2)
print("2. Updated VM POS History Server Script to query POS Invoice directly:", res2.status)
