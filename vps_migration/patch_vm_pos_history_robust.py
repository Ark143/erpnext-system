import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

history_script = """
def vm_pos_history():
    user = frappe.session.user
    is_manager = (user == 'Administrator') or bool(frappe.db.get_value('Has Role', {'parent': user, 'role': ['in', ['System Manager', 'Accounts Manager']], 'parenttype': 'User'}, 'name'))
    
    filters = [['docstatus', '<', 2]]
    
    company = (frappe.form_dict.get('company') or '').strip()
    if company and company not in ['All Branches', 'All', 'null', 'undefined', 'None']:
        filters.append(['company', '=', company])
    elif not is_manager and user != 'Guest':
        cashier_company = frappe.db.get_value('Employee', {'user_id': user}, 'company') or frappe.db.get_value('Cashier Profile', user, 'company')
        if cashier_company:
            filters.append(['company', '=', cashier_company])
    
    period = (frappe.form_dict.get('period') or 'all').strip().lower()
    from_date = (frappe.form_dict.get('from_date') or '').strip()
    to_date = (frappe.form_dict.get('to_date') or '').strip()
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
    
    search = (frappe.form_dict.get('search') or '').strip()
    or_filters = None
    if search:
        like = f'%{search}%'
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

# Update VM POS History with allow_guest=1
payload = {
    'script': history_script,
    'allow_guest': 1
}

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote('VM POS History'),
    data=json.dumps(payload).encode(),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)
res = opener.open(req)
print("Updated VM POS History (allow_guest=1, robust company filter):", res.status)
