"""
Deploy updated POS Shift backend Server Scripts:
1. VM POS Cashier: returns accurate cashier employee company and details
2. VM POS Get Shift: returns all companies and POS Profiles so cashier can select their company
3. VM POS Open Shift: validates that POS Profile is registered in ERPNext for the company before opening
"""
import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# 1. VM POS Cashier
script_cashier = """
def vm_pos_cashier():
    user = frappe.session.user
    out = {
        "user": user,
        "email": user,
        "company": None,
        "employee": None,
        "employee_name": None,
        "employee_number": None,
        "designation": None,
        "branch": None,
        "department": None,
        "reports_to": None,
        "enabled": 1
    }
    
    emp = frappe.db.get_value(
        "Employee",
        {"user_id": user},
        ["name", "employee_name", "employee_number", "designation", "branch", "department", "reports_to", "company"],
        as_dict=True
    )
    if emp:
        out["employee"] = emp.get("name")
        out["employee_name"] = emp.get("employee_name")
        out["employee_number"] = emp.get("employee_number")
        out["designation"] = emp.get("designation")
        out["branch"] = emp.get("branch")
        out["department"] = emp.get("department")
        out["reports_to"] = emp.get("reports_to")
        if emp.get("company"):
            out["company"] = emp["company"]
            
    if not out["company"]:
        cp = frappe.db.get_value("Cashier Profile", user, ["company", "enabled"], as_dict=True)
        if cp and cp.get("company"):
            out["company"] = cp["company"]
            out["enabled"] = cp.get("enabled", 1)
        else:
            out["company"] = frappe.db.get_single_value("Global Defaults", "default_company") or "ULTRA MRF"
            
    frappe.response["message"] = out

vm_pos_cashier()
"""

# 2. VM POS Get Shift
script_get_shift = """
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
        
        open_invs = [i for i in today_invs if not i.get('consolidated_invoice')]
        today_sales = sum(float(i.get('grand_total') or 0) for i in open_invs)
        existing['total_sales'] = today_sales
        existing['total_invoices'] = len(open_invs)
        existing['expected_closing'] = opening_amt + today_sales
        existing['shift_invoices'] = [i['name'] for i in open_invs]
        existing['cashier_user'] = user
        
        frappe.response['message'] = {'has_open_shift': True, 'shift': existing}
    else:
        # Resolve Cashier's designated default company
        default_company = None
        emp = frappe.db.get_value(
            'Employee',
            {'user_id': user},
            ['name', 'employee_name', 'company', 'branch', 'designation'],
            as_dict=True
        )
        if emp and emp.get('company'):
            default_company = emp['company']
        if not default_company:
            cp_company = frappe.db.get_value('Cashier Profile', user, 'company')
            if cp_company:
                default_company = cp_company
        if not default_company:
            default_company = frappe.db.get_single_value('Global Defaults', 'default_company') or 'ULTRA MRF'
            
        # Get all non-group companies for the dropdown
        all_companies = [
            c['name'] for c in frappe.get_all('Company', filters={'is_group': 0}, fields=['name'], order_by='name asc')
        ]
        
        # Get all enabled POS Profiles in ERPNext
        pos_profiles = frappe.get_all(
            'POS Profile',
            filters={'disabled': 0},
            fields=['name', 'company', 'warehouse'],
            order_by='company asc, name asc',
            limit=100
        )
        
        # Check user-level restrictions on profiles
        accessible_profiles = []
        for p in pos_profiles:
            app_users = frappe.get_all('POS Profile User', filters={'parent': p['name']}, fields=['user'])
            if not app_users or any(u['user'] == user for u in app_users):
                accessible_profiles.append({
                    'name': p['name'],
                    'company': p['company'],
                    'warehouse': p.get('warehouse') or ''
                })
                
        mops = frappe.get_all(
            'Mode of Payment',
            filters={'enabled': 1},
            fields=['name', 'type'],
            order_by='name asc',
            limit=20
        )
        
        frappe.response['message'] = {
            'has_open_shift': False,
            'shift': None,
            'companies': all_companies,
            'default_company': default_company,
            'profiles': accessible_profiles,
            'modes_of_payment': mops,
            'cashier_user': user,
            'cashier_details': {
                'employee': emp.get('name') if emp else None,
                'employee_name': emp.get('employee_name') if emp else None,
                'designation': emp.get('designation') if emp else None,
                'branch': emp.get('branch') if emp else None,
                'company': default_company
            }
        }

vm_pos_get_shift()
"""

# 3. VM POS Open Shift
script_open_shift = """
def vm_pos_open_shift():
    d = frappe.form_dict.get('data') or frappe.form_dict
    if isinstance(d, str):
        d = json.loads(d)
    
    user = d.get('user') or frappe.session.user
    if user == 'Guest':
        user = 'Administrator'
        
    company = (d.get('company') or '').strip()
    if not company:
        frappe.throw('Company is required to open a POS shift.')
        
    opening_amount = float(d.get('opening_amount') or 0)
    mop = (d.get('mode_of_payment') or 'Cash').strip()
    if not frappe.db.exists('Mode of Payment', mop):
        mop = 'Cash'
        
    profile_name = (d.get('pos_profile') or '').strip()
    
    # User requirement: Must have POS Profile first; if not, throw Error telling to register it first!
    if not profile_name:
        # Check if a default POS Profile exists for this company
        profile_name = frappe.db.get_value('POS Profile', {'company': company, 'disabled': 0}, 'name')
        
    if not profile_name:
        frappe.throw(
            f"No POS Profile found for company '{company}'. "
            "Please register a POS Profile in ERPNext first before opening a shift."
        )
        
    # Verify profile exists and is enabled for this company
    prof_exists = frappe.db.exists('POS Profile', {'name': profile_name, 'company': company, 'disabled': 0})
    if not prof_exists:
        frappe.throw(
            f"POS Profile '{profile_name}' is not registered or disabled for '{company}'. "
            "Please register a valid POS Profile in ERPNext first."
        )
        
    # Check if cashier already has an active open shift on this or another profile
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

    # Create fresh submitted POS Opening Entry using standard ERPNext doctype
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

scripts_to_update = {
    'VM POS Cashier': script_cashier,
    'VM POS Get Shift': script_get_shift,
    'VM POS Open Shift': script_open_shift,
}

H = {'Content-Type': 'application/json', 'Accept': 'application/json'}

for name, script_content in scripts_to_update.items():
    url = 'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote(name)
    payload = json.dumps({'script': script_content}).encode()
    req = urllib.request.Request(url, data=payload, headers=H, method='PUT')
    res = opener.open(req)
    print(f'Updated {name}: Status {res.status}')

print('\nAll Server Scripts updated successfully!')
