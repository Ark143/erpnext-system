import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# ─────────────────────────────────────────────────────────────────────────────
# 1. Update Server Script: VM POS Get Shift (Strictly per-cashier, per-day)
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
        
        # Calculate TODAY'S sales STRICTLY FOR THIS SPECIFIC CASHIER (owner == user)
        today_str = frappe.utils.today()
        today_invs = frappe.get_all(
            'POS Invoice',
            filters={
                'owner': user,
                'posting_date': today_str,
                'docstatus': 1
            },
            fields=['name', 'grand_total', 'paid_amount', 'posting_date', 'creation', 'customer', 'owner']
        )
        
        today_sales = sum(float(i.get('grand_total') or 0) for i in today_invs)
        existing['total_sales'] = today_sales
        existing['total_invoices'] = len(today_invs)
        existing['expected_closing'] = opening_amt + today_sales
        existing['shift_invoices'] = [i['name'] for i in today_invs]
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
print("1. Updated VM POS Get Shift: strictly per-cashier, per-day.")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Update Server Script: VM POS Create Invoice (Strict cashier ownership)
# ─────────────────────────────────────────────────────────────────────────────
create_invoice_script = """
def vm_pos_create_invoice():
    d = frappe.form_dict.get('data') or frappe.form_dict
    if isinstance(d, str):
        d = json.loads(d)
    
    user = d.get('user') or frappe.session.user
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
    
    # Check if cashier has an ACTIVE open shift
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
        
        # Create opening entry for this specific cashier if none exists
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
    inv.owner = user
    inv.insert(ignore_permissions=True)
    inv.submit()
    
    # Explicitly guarantee owner matches the cashier user
    if inv.owner != user:
        frappe.db.set_value('POS Invoice', inv.name, 'owner', user, update_modified=False)
        
    frappe.db.commit()

    frappe.response['message'] = {
        'name': inv.name,
        'pos_invoice': inv.name,
        'grand_total': inv.grand_total,
        'paid_amount': inv.paid_amount,
        'payment_method': mop,
        'cashier': user,
        'status': inv.status
    }

vm_pos_create_invoice()
"""

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/' + urllib.parse.quote('VM POS Create Invoice'),
    data=json.dumps({'script': create_invoice_script, 'allow_guest': 1}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PUT'
)
opener.open(req)
print("2. Updated VM POS Create Invoice: enforces explicit cashier ownership on every invoice.")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Update Server Script: VM POS Close Shift (Reconciles only this cashier today)
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
    
    # Strictly capture submitted POS Invoices for THIS SPECIFIC CASHIER today (owner == cashier_user)
    today_str = frappe.utils.today()
    invoices = frappe.get_all('POS Invoice',
        filters={
            'owner': cashier_user,
            'posting_date': today_str,
            'docstatus': 1
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
print("3. Updated VM POS Close Shift: reconciles strictly this cashier's invoices today.")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Patch current_pos_terminal.html (charge passes user, modal displays cashier breakdown)
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Updating current_pos_terminal.html ---")
with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix in charge(): pass user/cashier in payload
old_charge = """    const payload = {
      customer: this.customer || null,
      vehicle: this.vehicle || null,
      company: this.company,
      paid_amount: paid,
      payment_method: this.payment_method || "Cash",
      remarks: remarks,
      items: items
    };"""

new_charge = """    const payload = {
      user: this.cashier || this.user || "Administrator",
      customer: this.customer || null,
      vehicle: this.vehicle || null,
      company: this.company,
      paid_amount: paid,
      payment_method: this.payment_method || "Cash",
      remarks: remarks,
      items: items
    };"""

if old_charge in html:
    html = html.replace(old_charge, new_charge)
    print("4. Injected user/cashier into charge() payload.")

# Fix in showCloseShiftModal: display cashier name & branch explicitly
old_modal_start = '  async showCloseShiftModal() {'
old_modal_end = '  openScanner() {'
idx1 = html.find(old_modal_start)
idx2 = html.find(old_modal_end, idx1)

new_modal_code = """  async showCloseShiftModal() {
    const self = this;
    const overlay = document.createElement("div");
    overlay.className = "vpos-closing-overlay";
    overlay.innerHTML = `<div class="vpos-closing-modal" style="text-align:center;padding:36px;color:#c9d1d9;">⏳ Calculating cashier's daily sales...</div>`;
    document.body.appendChild(overlay);

    const cashierId = this.cashier || this.user || "Administrator";
    const cashierDisplayName = this.empName || this.cashier || this.user || "Administrator";

    // Fetch live shift & today's sales metrics for THIS cashier
    const shiftRes = await api("vm_pos_get_shift", {
      company: this.company || "ULTRA MRF",
      user: cashierId
    });

    if (!shiftRes || !shiftRes.has_open_shift) {
      overlay.remove();
      alert("No active shift found. Please enter your opening cash amount to start your shift.");
      await this.checkOrOpenShift();
      return;
    }

    const shift = shiftRes.shift;
    self.openingEntry = shift.name;
    self.openingAmount = parseFloat(shift.opening_amount || 0);
    self.shiftMop = shift.mode_of_payment || "Cash";
    self.posProfile = shift.pos_profile;

    // Strict cashier daily metrics
    const totalCollected = parseFloat(shift.total_sales || 0);
    const invoiceCount = parseInt(shift.total_invoices || 0);
    const expectedClose = parseFloat(shift.expected_closing || (self.openingAmount + totalCollected));
    const peso = v => "₱ " + parseFloat(v||0).toLocaleString("en-PH", {minimumFractionDigits:2, maximumFractionDigits:2});
    const todayFormatted = new Date().toLocaleDateString("en-PH", { month: "short", day: "numeric", year: "numeric" });
    const branchName = this.company || shift.company || "ULTRA MRF";

    overlay.innerHTML = `<div class="vpos-closing-modal">
      <div class="vpos-closing-title">🔴 Close Shift & Daily Reconciliation</div>
      <div class="vpos-closing-sub">Daily Shift Summary (${todayFormatted})</div>

      <div class="vpos-shift-info" style="margin-bottom:14px;background:#161b22;border:1px solid #30363d;border-radius:10px;padding:10px 14px;font-size:12px;line-height:1.6;">
        <div><strong>👤 Cashier:</strong> ${cashierDisplayName} <span style="opacity:0.6">(${cashierId})</span></div>
        <div><strong>🏢 Branch:</strong> ${branchName}</div>
        <div><strong>🎫 Shift Entry:</strong> ${shift.name}</div>
      </div>

      <div class="vpos-summary-row"><span class="lbl">Opening Cash Float</span><span class="amt">${peso(self.openingAmount)}</span></div>
      <div class="vpos-summary-row"><span class="lbl">Cashier's Today Sales</span><span class="amt pos" style="font-size:16px;font-weight:700;">${peso(totalCollected)}</span></div>
      <div class="vpos-summary-row"><span class="lbl">Cashier's Today Invoices</span><span class="amt">${invoiceCount} invoice${invoiceCount === 1 ? '' : 's'}</span></div>
      <div class="vpos-summary-row"><span class="lbl">Expected Cash in Drawer</span><span class="amt" style="font-size:16px;color:#16c784;font-weight:800;">${peso(expectedClose)}</span></div>

      <div class="vpos-shift-label" style="margin-top:18px">Actual Cash Count (₱)</div>
      <input class="vpos-shift-input" id="closing-amount" type="number" min="0" step="0.01"
             placeholder="Count your cash drawer and enter total" value="${expectedClose.toFixed(2)}">

      <div id="closing-diff-row" style="margin-top:10px;font-size:13px;font-weight:700;color:#16c784;text-align:right;">
        Difference: <span id="closing-diff-val">₱ 0.00 (Balanced)</span>
      </div>

      <div style="display:flex;gap:10px;margin-top:20px">
        <button class="vpos-shift-btn" id="shift-close-confirm">🔴 Submit & Close Shift</button>
        <button class="vpos-shift-btn" id="shift-close-cancel" style="background:#30363d;box-shadow:none;flex:0 0 auto;width:auto;padding:14px 20px">Cancel</button>
      </div>
      <div class="vpos-shift-err" id="closing-err"></div>
    </div>`;

    const countInput = overlay.querySelector("#closing-amount");
    const diffVal = overlay.querySelector("#closing-diff-val");
    
    const updateDiff = () => {
      const act = parseFloat(countInput.value) || 0;
      const diff = act - expectedClose;
      if (Math.abs(diff) < 0.01) {
        diffVal.textContent = "₱ 0.00 (Balanced)";
        diffVal.style.color = "#16c784";
      } else if (diff > 0) {
        diffVal.textContent = "+ " + peso(diff) + " (Overage)";
        diffVal.style.color = "#38bdf8";
      } else {
        diffVal.textContent = "- " + peso(Math.abs(diff)) + " (Shortage)";
        diffVal.style.color = "#f85149";
      }
    };
    countInput.oninput = updateDiff;
    updateDiff();

    overlay.querySelector("#shift-close-cancel").onclick = () => overlay.remove();
    overlay.querySelector("#shift-close-confirm").onclick = async () => {
      const btn = overlay.querySelector("#shift-close-confirm");
      const errEl = overlay.querySelector("#closing-err");
      btn.disabled = true; btn.textContent = "⏳ Closing shift...";
      errEl.textContent = "";
      try {
        const closing_amount = parseFloat(countInput.value) || 0;
        const result = await api("vm_pos_close_shift", {
          data: JSON.stringify({
            opening_entry: self.openingEntry,
            closing_amount,
            mode_of_payment: self.shiftMop || "Cash",
            user: cashierId
          })
        });
        if (result && result.name) {
          overlay.remove();
          alert("✅ Shift Closed Successfully!\\n\\n" +
            "Closing Entry: " + result.name + "\\n" +
            "Cashier: " + (result.cashier || cashierDisplayName) + "\\n" +
            "Invoices by Cashier Today: " + result.total_invoices + "\\n" +
            "Today's Sales: " + peso(result.grand_total) + "\\n" +
            "Opening Float: " + peso(result.opening_amount) + "\\n" +
            "Cash Counted: " + peso(result.closing_amount) + "\\n" +
            "Difference: " + peso(result.difference));
          self.openingEntry = null;
          self.openingAmount = 0;
          self.logout();
        } else {
          const err = api.lastError || "Failed to close shift. Check ERPNext logs.";
          errEl.textContent = "Error: " + err;
          btn.disabled = false; btn.textContent = "🔴 Submit & Close Shift";
        }
      } catch(e) {
        errEl.textContent = "Error: " + (e.message || e);
        btn.disabled = false; btn.textContent = "🔴 Submit & Close Shift";
      }
    };
  },

"""

if idx1 != -1 and idx2 != -1:
    html = html[:idx1] + new_modal_code + html[idx2:]
    print("5. Injected enhanced cashier-isolated showCloseShiftModal() into HTML.")
else:
    print("5. Warning: showCloseShiftModal indices not found.")

# Save local files
with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("6. Saved local HTML files.")

# Deploy to Web Page
save_url = 'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal'
payload = json.dumps({'main_section_html': html}).encode('utf-8')
req = urllib.request.Request(save_url, data=payload, headers={'Content-Type': 'application/json'}, method='PUT')
res = opener.open(req)
print(f"7. Successfully deployed to Web Page/vehicle-pos-terminal: HTTP {res.status}")
