import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# ─────────────────────────────────────────────────────────────────────────────
# Update VM POS Open Shift to support multiple cashiers in the same company
# ─────────────────────────────────────────────────────────────────────────────
open_shift_script = """
def vm_pos_open_shift():
    d = frappe.form_dict.get('data') or frappe.form_dict
    if isinstance(d, str):
        d = json.loads(d)
    
    user = d.get('user') or frappe.session.user
    if user == 'Guest':
        user = 'Administrator'
    
    company = (d.get('company') or frappe.defaults.get_user_default('Company') or 'ULTRA MRF').strip()
    if company in ['All Branches', 'All', 'null', 'undefined', '', None]:
        company = 'ULTRA MRF'
        
    opening_amount = float(d.get('opening_amount') or 0)
    mop = (d.get('mode_of_payment') or 'Cash').strip()
    
    if not frappe.db.exists('Mode of Payment', mop):
        mop = 'Cash'
    
    # 1. Resolve or dynamically create a POS Profile for this cashier
    profile_name = d.get('pos_profile')
    
    # If the requested profile is currently open by a DIFFERENT user, give this cashier their own profile!
    in_use_by_other = False
    if profile_name:
        in_use_by_other = frappe.db.exists(
            'POS Opening Entry',
            {'pos_profile': profile_name, 'status': 'Open', 'docstatus': 1, 'user': ['!=', user]}
        )
        
    if not profile_name or in_use_by_other:
        clean_user = user.split('@')[0].replace('.', ' ').title()
        candidate = f'POS - {company} - {clean_user}'
        if frappe.db.exists('POS Profile', candidate):
            profile_name = candidate
        else:
            # Clone from existing profile in company or create fresh
            base_prof = frappe.db.get_value('POS Profile', {'company': company, 'disabled': 0}, 'name')
            if base_prof:
                base_doc = frappe.get_doc('POS Profile', base_prof)
                prof = frappe.copy_doc(base_doc)
                prof.name = candidate
                prof.pos_profile_name = candidate
                prof.applicable_for_users = []
                prof.append('applicable_for_users', {'user': user, 'default': 1})
                prof.insert(ignore_permissions=True)
                profile_name = prof.name
            else:
                default_warehouse = (
                    frappe.db.get_value('Company', company, 'default_fg_warehouse')
                    or frappe.db.get_value('Warehouse', {'company': company, 'is_group': 0}, 'name')
                )
                income_account = frappe.db.get_value('Company', company, 'default_income_account')
                cost_center = (
                    frappe.db.get_value('Company', company, 'cost_center')
                    or frappe.db.get_value('Cost Center', {'company': company, 'is_group': 0}, 'name')
                )
                prof = frappe.get_doc({
                    'doctype': 'POS Profile',
                    'name': candidate,
                    'company': company,
                    'warehouse': default_warehouse,
                    'currency': frappe.db.get_value('Company', company, 'default_currency') or 'PHP',
                    'income_account': income_account,
                    'cost_center': cost_center,
                    'payments': [{'default': 1, 'mode_of_payment': mop}],
                    'write_off_account': income_account,
                    'write_off_cost_center': cost_center,
                    'applicable_for_users': [{'user': user, 'default': 1}]
                })
                prof.insert(ignore_permissions=True)
                profile_name = prof.name
    
    # 2. Check if this cashier already has an open entry on this profile
    already_open = frappe.db.get_value(
        'POS Opening Entry',
        {'user': user, 'status': 'Open', 'docstatus': 1},
        ['name', 'pos_profile', 'company'],
        as_dict=True
    )
    if already_open:
        balance = frappe.db.get_value(
            'POS Opening Entry Detail',
            {'parent': already_open['name']},
            ['mode_of_payment', 'opening_amount'],
            as_dict=True
        )
        frappe.response['message'] = {
            'name': already_open['name'],
            'pos_profile': already_open['pos_profile'],
            'company': already_open['company'],
            'opening_amount': float(balance['opening_amount'] if balance else 0),
            'mode_of_payment': balance['mode_of_payment'] if balance else 'Cash',
            'status': 'Open'
        }
        return

    # 3. Create fresh submitted POS Opening Entry for this cashier
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
        'cashier': user,
        'status': 'Open'
    }

vm_pos_open_shift()
"""

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote('VM POS Open Shift'),
    data=json.dumps({'script': open_shift_script, 'allow_guest': 1}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)
opener.open(req)
print("Updated VM POS Open Shift: supports multiple simultaneous cashiers per branch with dedicated profiles.")
