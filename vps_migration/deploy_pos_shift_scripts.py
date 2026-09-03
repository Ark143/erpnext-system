"""
Deploy POS Opening / Closing Entry backend Server Scripts.
These call ERPNext's standard POS Opening Entry and POS Closing Entry doctypes.
"""
import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# =========================================================================
# 1. vm_pos_get_shift  — check if there is an active open shift for this user
# =========================================================================
get_shift_script = """
def vm_pos_get_shift():
    user = frappe.session.user
    company = frappe.form_dict.get('company') or frappe.defaults.get_user_default('Company')
    
    # Find existing open POS Opening Entry for this cashier
    filters = {'user': user, 'status': 'Open', 'docstatus': 1}
    if company:
        filters['company'] = company
    
    existing = frappe.db.get_value(
        'POS Opening Entry',
        filters,
        ['name', 'pos_profile', 'company', 'posting_date', 'period_start_date',
         'set_posting_date', 'pos_closing_entry'],
        as_dict=True
    )
    
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
        profiles = frappe.get_all('POS Profile', 
            filters={'disabled': 0, 'company': company} if company else {'disabled': 0},
            fields=['name', 'company'],
            limit=10
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

# =========================================================================
# 2. vm_pos_open_shift  — create POS Opening Entry (standard ERPNext)
# =========================================================================
open_shift_script = """
def vm_pos_open_shift():
    user = frappe.session.user
    d = frappe.form_dict.get('data') or frappe.form_dict
    if isinstance(d, str):
        d = json.loads(d)
    
    company = d.get('company') or frappe.defaults.get_user_default('Company')
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
        # Auto-create minimal POS Profile
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
            prof = frappe.get_doc({
                'doctype': 'POS Profile',
                'name': profile_name,
                'company': company,
                'warehouse': default_warehouse,
                'currency': frappe.db.get_value('Company', company, 'default_currency') or 'PHP',
                'income_account': income_account,
                'cost_center': cost_center,
                'payments': [{'default': 1, 'mode_of_payment': mop}],
                'write_off_account': income_account,
                'write_off_cost_center': cost_center
            })
            prof.insert(ignore_permissions=True)
    
    # Close any stale open entries for this user (different company or profile)
    stale = frappe.get_all('POS Opening Entry',
        filters={'user': user, 'status': 'Open', 'docstatus': 1},
        fields=['name']
    )
    for s in stale:
        frappe.db.set_value('POS Opening Entry', s.name, 'status', 'Closed', update_modified=False)
    
    # Create fresh POS Opening Entry
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
        'opening_amount': opening_amount,
        'mode_of_payment': mop,
        'period_start_date': str(entry.period_start_date),
        'status': 'Open'
    }

vm_pos_open_shift()
"""

# =========================================================================
# 3. vm_pos_close_shift  — create POS Closing Entry (standard ERPNext)
# =========================================================================
close_shift_script = """
def vm_pos_close_shift():
    user = frappe.session.user
    d = frappe.form_dict.get('data') or frappe.form_dict
    if isinstance(d, str):
        d = json.loads(d)
    
    opening_entry_name = d.get('opening_entry')
    closing_amount = float(d.get('closing_amount') or 0)
    mop = d.get('mode_of_payment') or 'Cash'
    
    if not opening_entry_name:
        frappe.throw('POS Opening Entry name is required.')
    
    opening = frappe.get_doc('POS Opening Entry', opening_entry_name)
    if opening.status != 'Open':
        frappe.throw(f'Shift {opening_entry_name} is already closed.')
    
    # Get all submitted POS Invoices for this shift
    invoices = frappe.get_all('POS Invoice',
        filters={
            'owner': user,
            'company': opening.company,
            'docstatus': 1,
            'creation': ['>=', str(opening.period_start_date)]
        },
        fields=['name', 'grand_total', 'net_total', 'posting_date', 'customer'],
        order_by='creation asc',
        limit_page_length=1000
    )
    
    net_total = sum(float(i.get('net_total') or 0) for i in invoices)
    grand_total = sum(float(i.get('grand_total') or 0) for i in invoices)
    
    # Get opening balance from balance_details child
    opening_balance = float(
        frappe.db.get_value('POS Opening Entry Detail', {'parent': opening_entry_name}, 'opening_amount') or 0
    )
    
    # Build closing entry using correct field names
    closing_doc = frappe.get_doc({
        'doctype': 'POS Closing Entry',
        'company': opening.company,
        'pos_profile': opening.pos_profile,
        'user': user,
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
            'expected_amount': opening_balance + grand_total,
            'closing_amount': closing_amount,
            'difference': closing_amount - (opening_balance + grand_total)
        }],
        'taxes': []
    })
    closing_doc.insert(ignore_permissions=True)
    closing_doc.submit()
    
    # Mark opening entry as closed
    frappe.db.set_value('POS Opening Entry', opening_entry_name, 'status', 'Closed', update_modified=False)
    frappe.db.commit()
    
    frappe.response['message'] = {
        'name': closing_doc.name,
        'opening_entry': opening_entry_name,
        'total_invoices': len(invoices),
        'grand_total': grand_total,
        'opening_amount': opening_balance,
        'closing_amount': closing_amount,
        'difference': closing_amount - (opening_balance + grand_total),
        'status': 'Closed'
    }

vm_pos_close_shift()
"""

def upsert_script(api_method, script_code, label):
    """Create or update a Server Script."""
    # Check if it exists
    check_url = f'http://38.247.138.224:10017/api/resource/Server%20Script/{urllib.parse.quote(api_method.upper() + " SS")}'
    # Use lowercase api_method as the document name
    name = api_method + '_ss'
    
    # Build payload
    payload = {
        'doctype': 'Server Script',
        'script_type': 'API',
        'api_method': api_method,
        'allow_guest': 0,
        'disabled': 0,
        'script': script_code
    }
    
    # Try PUT first (update), fallback to POST (create)
    try:
        r = opener.open(urllib.request.Request(
            f'http://38.247.138.224:10017/api/resource/Server%20Script/{urllib.parse.quote(label)}',
            data=json.dumps({'script': script_code}).encode(),
            headers={'Content-Type': 'application/json'},
            method='PUT'
        ))
        print(f"  UPDATED {label}: {r.status}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Create new
            r = opener.open(urllib.request.Request(
                'http://38.247.138.224:10017/api/resource/Server%20Script',
                data=json.dumps(payload | {'name': label}).encode(),
                headers={'Content-Type': 'application/json'},
                method='POST'
            ))
            print(f"  CREATED {label}: {r.status}")
        else:
            print(f"  ERROR {label}: {e.code} {e.read().decode()[:200]}")

print("Deploying POS Shift Server Scripts...")

upsert_script('vm_pos_get_shift', get_shift_script, 'VM POS Get Shift')
upsert_script('vm_pos_open_shift', open_shift_script, 'VM POS Open Shift')
upsert_script('vm_pos_close_shift', close_shift_script, 'VM POS Close Shift')

print("Done!")
