import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# ─────────────────────────────────────────────────────────────────────────────
# 1. Update Server Script: VM POS Get Shift (guarantee shift resumption)
# ─────────────────────────────────────────────────────────────────────────────
get_shift_script = """
def vm_pos_get_shift():
    user = frappe.form_dict.get('user') or frappe.session.user
    if user == 'Guest':
        user = 'Administrator'
    
    # 1. Check for ANY active open shift for this user (ignore company filter so cashier always resumes!)
    existing = frappe.db.get_value(
        'POS Opening Entry',
        {'user': user, 'status': 'Open', 'docstatus': 1},
        ['name', 'pos_profile', 'company', 'posting_date', 'period_start_date',
         'set_posting_date', 'pos_closing_entry'],
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
        
        # Calculate real-time sales in this shift
        shift_invs = frappe.get_all(
            'POS Invoice',
            filters={
                'owner': user,
                'pos_profile': existing['pos_profile'],
                'docstatus': 1,
                'creation': ['>=', str(existing['period_start_date'])]
            },
            fields=['name', 'grand_total', 'paid_amount', 'posting_date', 'creation', 'customer']
        )
        shift_sales = sum(float(i.get('grand_total') or 0) for i in shift_invs)
        existing['total_sales'] = shift_sales
        existing['total_invoices'] = len(shift_invs)
        existing['expected_closing'] = opening_amt + shift_sales
        existing['shift_invoices'] = [i['name'] for i in shift_invs]
        
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
            'company': company
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
print("1. Updated VM POS Get Shift: always resumes open shift regardless of company mismatch.")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Update Server Script: VM POS Create Invoice (NEVER prematurely close open shifts)
# ─────────────────────────────────────────────────────────────────────────────
create_script = """
def vm_pos_create_invoice():
    d = frappe.form_dict.get('data') or frappe.form_dict
    if isinstance(d, str):
        d = json.loads(d)
    
    user = frappe.session.user
    if user == 'Guest':
        user = 'Administrator'
        
    cust = d.get('customer')
    veh = d.get('vehicle')
    plate = ''
    if veh and frappe.db.exists('Customer Vehicle', veh):
        veh_row = frappe.db.get_value('Customer Vehicle', veh, ['customer', 'plate_no'], as_dict=True)
        if veh_row:
            if veh_row.get('customer'):
                cust = veh_row['customer']
            plate = veh_row.get('plate_no') or ''
    
    # Check if cashier has an ACTIVE open shift: adopt its pos_profile and company!
    active_shift = frappe.db.get_value(
        'POS Opening Entry',
        {'user': user, 'status': 'Open', 'docstatus': 1},
        ['name', 'pos_profile', 'company'],
        as_dict=True
    )
    
    if active_shift:
        company = active_shift['company']
        profile_name = active_shift['pos_profile']
    else:
        company = d.get('company') or frappe.defaults.get_user_default('Company') or 'ULTRA MRF'
        if company in ['All Branches', 'All', 'null', 'undefined']:
            company = 'ULTRA MRF'
        profile_name = frappe.db.get_value('POS Profile', {'company': company, 'disabled': 0}, 'name') or frappe.db.get_value('POS Profile', {'company': company}, 'name')
        if not profile_name:
            profile_name = f'Vehicle POS - {company}'
        
        # Only create opening entry if none exists at all; NEVER close other shifts!
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

    # Resolve Mode of Payment
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
opener.open(req)
print("2. Updated VM POS Create Invoice: NEVER closes active open shift; links directly.")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Patch current_pos_terminal.html: checkOrOpenShift resumes seamlessly
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Updating checkOrOpenShift in HTML ---")
with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_check = """  async checkOrOpenShift() {
    const shift = await api("vm_pos_get_shift", { company: this.company || "" });
    if (shift && shift.has_open_shift) {
      // Cashier has an active shift — go straight to POS
      this.openingEntry = shift.shift.name;
      this.openingAmount = shift.shift.opening_amount;
      this.shiftMop = shift.shift.mode_of_payment;
      this.posProfile = shift.shift.pos_profile;
      this.build();
      this.load();
    } else {
      // No active shift — show Opening Entry screen
      this._shiftMeta = shift; // holds profiles, modes_of_payment
      this.buildOpeningEntry(shift);
    }
  },"""

new_check = """  async checkOrOpenShift() {
    const shift = await api("vm_pos_get_shift", {
      company: this.company || "",
      user: this.cashier || this.user || ""
    });
    if (shift && shift.has_open_shift) {
      // Cashier already has an active open shift — RESUME CASHIERING DIRECTLY
      this.openingEntry = shift.shift.name;
      this.openingAmount = parseFloat(shift.shift.opening_amount || 0);
      this.shiftMop = shift.shift.mode_of_payment || "Cash";
      this.posProfile = shift.shift.pos_profile;
      if (shift.shift.company) this.company = shift.shift.company;
      this.build();
      this.load();
    } else {
      // No active shift — prompt for opening float
      this._shiftMeta = shift;
      this.buildOpeningEntry(shift);
    }
  },"""

if old_check in html:
    html = html.replace(old_check, new_check)
    print("3. Injected seamless shift resumption in checkOrOpenShift().")
else:
    print("3. Warning: checkOrOpenShift pattern differed.")

# Save local files
with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("4. Saved local HTML files.")

# Deploy to Web Page
save_url = 'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal'
payload = json.dumps({'main_section_html': html}).encode('utf-8')
req = urllib.request.Request(save_url, data=payload, headers={'Content-Type': 'application/json'}, method='PUT')
res = opener.open(req)
print(f"5. Successfully deployed to Web Page/vehicle-pos-terminal: HTTP {res.status}")
