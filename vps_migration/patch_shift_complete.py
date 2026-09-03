import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# ─────────────────────────────────────────────────────────────────────────────
# 1. Update Server Script: VM POS Get Shift
# ─────────────────────────────────────────────────────────────────────────────
get_shift_script = """
def vm_pos_get_shift():
    user = frappe.form_dict.get('user') or frappe.session.user
    if user == 'Guest':
        user = 'Administrator'
    
    company = (frappe.form_dict.get('company') or frappe.defaults.get_user_default('Company') or 'ULTRA MRF').strip()
    if company in ['All Branches', 'All', 'null', 'undefined', '']:
        company = 'ULTRA MRF'
    
    # 1. Look for user's open shift in this company
    existing = frappe.db.get_value(
        'POS Opening Entry',
        {'user': user, 'company': company, 'status': 'Open', 'docstatus': 1},
        ['name', 'pos_profile', 'company', 'posting_date', 'period_start_date',
         'set_posting_date', 'pos_closing_entry'],
        as_dict=True
    )
    
    # 2. If not found, look for ANY open shift for this user
    if not existing:
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
        existing['opening_amount'] = float(balance['opening_amount'] if balance else 0)
        existing['mode_of_payment'] = balance['mode_of_payment'] if balance else 'Cash'
        frappe.response['message'] = {'has_open_shift': True, 'shift': existing}
    else:
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
print("1. Updated VM POS Get Shift (allow_guest=1)")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Update Server Script: VM POS Open Shift
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
    
    # Get or create POS Profile
    profile_name = d.get('pos_profile')
    if not profile_name or not frappe.db.exists('POS Profile', profile_name):
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
    
    # Close any other open entries for this user
    stale = frappe.get_all('POS Opening Entry',
        filters={'user': user, 'status': 'Open', 'docstatus': 1},
        fields=['name']
    )
    for s in stale:
        frappe.db.set_value('POS Opening Entry', s.name, 'status', 'Closed', update_modified=False)
    
    # Create submitted POS Opening Entry
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

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote('VM POS Open Shift'),
    data=json.dumps({'script': open_shift_script, 'allow_guest': 1}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)
opener.open(req)
print("2. Updated VM POS Open Shift (allow_guest=1)")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Update Server Script: VM POS Close Shift
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
    
    # Get all submitted POS Invoices for this shift
    invoices = frappe.get_all('POS Invoice',
        filters={
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
    
    opening_balance = float(
        frappe.db.get_value('POS Opening Entry Detail', {'parent': opening_entry_name}, 'opening_amount') or 0
    )
    
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

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote('VM POS Close Shift'),
    data=json.dumps({'script': close_shift_script, 'allow_guest': 1}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)
opener.open(req)
print("3. Updated VM POS Close Shift (allow_guest=1)")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Patch current_pos_terminal.html
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Patching current_pos_terminal.html ---")
with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix 1: Rail click handler for close-shift
old_rail_click = """      const act = b.getAttribute("data-action");
      if (act === "logout") { self.logout(); return; }
      self.switchView(b.getAttribute("data-view"));"""

new_rail_click = """      const act = b.getAttribute("data-action");
      if (act === "logout") { self.logout(); return; }
      if (act === "close-shift") { self.showCloseShiftModal(); return; }
      self.switchView(b.getAttribute("data-view"));"""

if old_rail_click in html:
    html = html.replace(old_rail_click, new_rail_click)
    print("  [Fix 1] Wired close-shift in navigation rail.")
else:
    print("  [Fix 1] Note: rail click pattern check...")

# Fix 2: Add Shift Badge and Close Shift button to top bar
old_top_bar = """            <div class="vpos-branch-row">
              <div class="vpos-branch-badge" title="Assigned Cashier Branch (Auto-detected from Employee Details)">
                <span class="vpos-branch-lbl">🏢 BRANCH:</span>
                <span class="vpos-branch-val" id="vpos-branch-name">${this.company || "All Branches"}</span>
              </div>
              <button class="vpos-stock-toggle" id="vpos-stock-toggle" title="Toggle in-stock filter">In Stock: OFF</button>
            </div>"""

new_top_bar = """            <div class="vpos-branch-row">
              <div class="vpos-branch-badge" title="Assigned Cashier Branch">
                <span class="vpos-branch-lbl">🏢 BRANCH:</span>
                <span class="vpos-branch-val" id="vpos-branch-name">${this.company || "ULTRA MRF"}</span>
              </div>
              <div class="vpos-shift-badge" id="vpos-shift-badge" title="Active Shift & Opening Cash" style="display:flex;align-items:center;gap:6px;background:rgba(22,199,132,0.12);border:1px solid rgba(22,199,132,0.3);border-radius:10px;padding:4px 10px;font-size:11.5px;color:#16c784;font-weight:700;">
                <span>🟢 SHIFT: <span id="vpos-shift-name-top">${this.openingEntry || 'Active'}</span></span>
                <span style="opacity:0.4">|</span>
                <span>Drawer: <span id="vpos-shift-drawer-top">₱${(this.openingAmount || 0).toLocaleString('en-US', {minimumFractionDigits:2})}</span></span>
                <button type="button" id="vpos-btn-top-close-shift" style="margin-left:4px;background:#f85149;color:#fff;border:none;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:700;cursor:pointer;">Close Shift</button>
              </div>
              <button class="vpos-stock-toggle" id="vpos-stock-toggle" title="Toggle in-stock filter">In Stock: OFF</button>
            </div>"""

if old_top_bar in html:
    html = html.replace(old_top_bar, new_top_bar)
    print("  [Fix 2] Added visible Shift Badge & Close Shift button to top bar.")
else:
    print("  [Fix 2] Note: old_top_bar pattern check...")

# Fix 3: Wire #vpos-btn-top-close-shift in build()
old_wire_stock = """    const st = r.querySelector("#vpos-stock-toggle");"""
new_wire_stock = """    const topCloseBtn = r.querySelector("#vpos-btn-top-close-shift");
    if (topCloseBtn) topCloseBtn.onclick = () => self.showCloseShiftModal();

    const st = r.querySelector("#vpos-stock-toggle");"""

if old_wire_stock in html:
    html = html.replace(old_wire_stock, new_wire_stock)
    print("  [Fix 3] Wired top bar close shift button click.")

# Fix 4: Upgrade showCloseShiftModal to auto-fetch open shift if this.openingEntry is missing
old_modal_check = """  showCloseShiftModal() {
    const self = this;
    if (!this.openingEntry) { alert("No active shift found."); return; }"""

new_modal_check = """  async showCloseShiftModal() {
    const self = this;
    if (!this.openingEntry) {
      const shiftRes = await api("vm_pos_get_shift", { company: this.company || "ULTRA MRF", user: this.cashier || this.user || "Administrator" });
      if (shiftRes && shiftRes.has_open_shift) {
        this.openingEntry = shiftRes.shift.name;
        this.openingAmount = shiftRes.shift.opening_amount;
        this.shiftMop = shiftRes.shift.mode_of_payment;
        this.posProfile = shiftRes.shift.pos_profile;
      } else {
        alert("No active shift found. Please enter your opening cash amount to start your shift.");
        await this.checkOrOpenShift();
        return;
      }
    }"""

if old_modal_check in html:
    html = html.replace(old_modal_check, new_modal_check)
    print("  [Fix 4] Upgraded showCloseShiftModal with auto-fetch fallback.")

# Save local files
with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("  Saved local HTML files.")

# Deploy to Web Page
save_url = 'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal'
payload = json.dumps({'main_section_html': html}).encode('utf-8')
req = urllib.request.Request(save_url, data=payload, headers={'Content-Type': 'application/json'}, method='PUT')
res = opener.open(req)
print(f"  SUCCESS! Deployed to Web Page/vehicle-pos-terminal: HTTP {res.status}")
