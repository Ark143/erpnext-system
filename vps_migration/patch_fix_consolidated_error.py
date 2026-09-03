import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# ─────────────────────────────────────────────────────────────────────────────
# 1. Update Server Script: VM POS Get Shift (Filters out already consolidated)
# ─────────────────────────────────────────────────────────────────────────────
get_shift_script = """
def vm_pos_get_shift():
    user = frappe.form_dict.get('user') or frappe.session.user
    if user == 'Guest':
        user = 'Administrator'
    
    # Strictly query for this specific cashier user's active open shift
    existing = frappe.db.get_value(
        'POS Opening Entry',
        {'user': user, 'status': 'Open', 'docstatus': 1},
        ['name', 'pos_profile', 'company', 'posting_date', 'period_start_date',
         'set_posting_date', 'pos_closing_entry', 'user'],
        as_dict=True
    )

    if existing:
        balance = frappe.db.get_value(
            'POS Opening Entry Detail',
            {'parent': existing['name']},
            ['mode_of_payment', 'opening_amount'],
            as_dict=True
        )
        opening_amt = float(balance['opening_amount'] if balance else 0)
        existing['opening_amount'] = opening_amt
        existing['mode_of_payment'] = balance['mode_of_payment'] if balance else 'Cash'
        
        # Calculate TODAY'S sales STRICTLY FOR THIS CASHIER that are NOT yet consolidated
        today_str = frappe.utils.today()
        today_invs = frappe.get_all(
            'POS Invoice',
            filters={
                'owner': user,
                'posting_date': today_str,
                'docstatus': 1
            },
            fields=['name', 'grand_total', 'paid_amount', 'posting_date', 'creation', 'customer', 'consolidated_invoice']
        )
        
        # Exclude already-consolidated invoices
        open_invs = [i for i in today_invs if not i.get('consolidated_invoice')]
        
        today_sales = sum(float(i.get('grand_total') or 0) for i in open_invs)
        existing['total_sales'] = today_sales
        existing['total_invoices'] = len(open_invs)
        existing['expected_closing'] = opening_amt + today_sales
        existing['shift_invoices'] = [i['name'] for i in open_invs]
        existing['cashier_user'] = user
        
        frappe.response['message'] = {'has_open_shift': True, 'shift': existing}
    else:
        company = (frappe.form_dict.get('company') or frappe.defaults.get_user_default('Company') or 'ULTRA MRF').strip()
        if company in ['All Branches', 'All', 'null', 'undefined', '']:
            company = 'ULTRA MRF'
            
        profiles = frappe.get_all('POS Profile',
            filters={'disabled': 0, 'company': company} if company else {'disabled': 0},
            fields=['name', 'company'],
            limit=10
        )
        if not profiles:
            profiles = frappe.get_all('POS Profile', filters={'disabled': 0}, fields=['name', 'company'], limit=10)
            
        mops = frappe.get_all('Mode of Payment',
            filters={'enabled': 1},
            fields=['name', 'type'],
            order_by='name asc',
            limit=20
        )
        frappe.response['message'] = {
            'has_open_shift': False,
            'shift': None,
            'profiles': profiles,
            'modes_of_payment': mops,
            'company': company,
            'cashier_user': user
        }

vm_pos_get_shift()
"""

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote('VM POS Get Shift'),
    data=json.dumps({'script': get_shift_script, 'allow_guest': 1}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)
opener.open(req)
print("1. Updated VM POS Get Shift (excludes already-consolidated invoices).")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Update Server Script: VM POS Close Shift (Excludes already-consolidated)
# ─────────────────────────────────────────────────────────────────────────────
close_shift_script = """
def vm_pos_close_shift():
    d = frappe.form_dict.get('data') or frappe.form_dict
    if isinstance(d, str):
        d = json.loads(d)
    
    user = d.get('user') or frappe.session.user
    if user == 'Guest':
        user = 'Administrator'
        
    opening_entry_name = d.get('opening_entry')
    if not opening_entry_name:
        opening_entry_name = frappe.db.get_value('POS Opening Entry', {'user': user, 'status': 'Open', 'docstatus': 1}, 'name')
    if not opening_entry_name:
        opening_entry_name = frappe.db.get_value('POS Opening Entry', {'status': 'Open', 'docstatus': 1}, 'name')
        
    if not opening_entry_name:
        frappe.throw('No active POS Opening Entry found to close.')
    
    opening = frappe.get_doc('POS Opening Entry', opening_entry_name)
    if opening.status != 'Open':
        frappe.throw(f'Shift {opening_entry_name} is already closed.')
    
    closing_amount = float(d.get('closing_amount') or 0)
    mop = d.get('mode_of_payment') or 'Cash'
    cashier_user = opening.user or user
    
    # Strictly capture UNCONSOLIDATED submitted POS Invoices for THIS Cashier today
    today_str = frappe.utils.today()
    all_invoices = frappe.get_all('POS Invoice',
        filters={
            'owner': cashier_user,
            'posting_date': today_str,
            'docstatus': 1
        },
        fields=['name', 'grand_total', 'net_total', 'posting_date', 'customer', 'consolidated_invoice'],
        order_by='creation asc',
        limit_page_length=1000
    )
    
    # Filter out invoices that are already consolidated into a Sales Invoice
    invoices = [i for i in all_invoices if not i.get('consolidated_invoice')]
    
    net_total = sum(float(i.get('net_total') or 0) for i in invoices)
    grand_total = sum(float(i.get('grand_total') or 0) for i in invoices)
    
    opening_balance = float(
        frappe.db.get_value('POS Opening Entry Detail', {'parent': opening_entry_name}, 'opening_amount') or 0
    )
    
    expected_amount = opening_balance + grand_total
    difference = closing_amount - expected_amount
    
    closing_doc = frappe.get_doc({
        'doctype': 'POS Closing Entry',
        'company': opening.company,
        'pos_profile': opening.pos_profile,
        'user': cashier_user,
        'pos_opening_entry': opening_entry_name,
        'period_start_date': opening.period_start_date,
        'period_end_date': frappe.utils.now_datetime(),
        'posting_date': frappe.utils.nowdate(),
        'grand_total': grand_total,
        'net_total': net_total,
        'pos_invoices': [{
            'pos_invoice': i['name'],
            'posting_date': str(i.get('posting_date') or frappe.utils.nowdate()),
            'customer': i.get('customer') or '',
            'grand_total': float(i.get('grand_total') or 0),
            'is_return': 0
        } for i in invoices],
        'payment_reconciliation': [{
            'mode_of_payment': mop,
            'opening_amount': opening_balance,
            'expected_amount': expected_amount,
            'closing_amount': closing_amount,
            'difference': difference
        }],
        'taxes': []
    })
    closing_doc.insert(ignore_permissions=True)
    closing_doc.submit()
    
    frappe.db.set_value('POS Opening Entry', opening_entry_name, 'status', 'Closed', update_modified=False)
    frappe.db.commit()
    
    frappe.response['message'] = {
        'name': closing_doc.name,
        'opening_entry': opening_entry_name,
        'cashier': cashier_user,
        'total_invoices': len(invoices),
        'grand_total': grand_total,
        'opening_amount': opening_balance,
        'closing_amount': closing_amount,
        'difference': difference,
        'status': 'Closed'
    }

vm_pos_close_shift()
"""

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote('VM POS Close Shift'),
    data=json.dumps({'script': close_shift_script, 'allow_guest': 1}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)
opener.open(req)
print("2. Updated VM POS Close Shift (filters out already-consolidated invoices).")
