import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# ─────────────────────────────────────────────────────────────────────────────
# 1. Update Server Script: VM POS Get Shift (computes shift sales in real time)
# ─────────────────────────────────────────────────────────────────────────────
get_shift_script = """
def vm_pos_get_shift():
    user = frappe.form_dict.get('user') or frappe.session.user
    if user == 'Guest':
        user = 'Administrator'
    
    company = (frappe.form_dict.get('company') or frappe.defaults.get_user_default('Company') or 'ULTRA MRF').strip()
    if company in ['All Branches', 'All', 'null', 'undefined', '']:
        company = 'ULTRA MRF'
    
    # 1. Look for user's open shift
    existing = frappe.db.get_value(
        'POS Opening Entry',
        {'user': user, 'company': company, 'status': 'Open', 'docstatus': 1},
        ['name', 'pos_profile', 'company', 'posting_date', 'period_start_date',
         'set_posting_date', 'pos_closing_entry'],
        as_dict=True
    )
    
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
        opening_amt = float(balance['opening_amount'] if balance else 0)
        existing['opening_amount'] = opening_amt
        existing['mode_of_payment'] = balance['mode_of_payment'] if balance else 'Cash'
        
        # Calculate SALES STRICTLY IN THIS SHIFT for this cashier
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
print("1. Updated VM POS Get Shift with real-time shift sales computation.")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Update Server Script: VM POS Close Shift (strictly shift-only invoices)
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
    
    # Strictly get submitted POS Invoices for THIS cashier and THIS shift
    invoices = frappe.get_all('POS Invoice',
        filters={
            'owner': opening.user,
            'pos_profile': opening.pos_profile,
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
    
    expected_amount = opening_balance + grand_total
    difference = closing_amount - expected_amount
    
    closing_doc = frappe.get_doc({
        'doctype': 'POS Closing Entry',
        'company': opening.company,
        'pos_profile': opening.pos_profile,
        'user': opening.user,
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
print("2. Updated VM POS Close Shift (shift-isolated invoices only).")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Patch showCloseShiftModal in current_pos_terminal.html
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Updating showCloseShiftModal in HTML ---")
with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the showCloseShiftModal method
old_modal_start = '  async showCloseShiftModal() {'
old_modal_end = '  openScanner() {'
idx1 = html.find(old_modal_start)
idx2 = html.find(old_modal_end, idx1)

new_modal_code = """  async showCloseShiftModal() {
    const self = this;
    const overlay = document.createElement("div");
    overlay.className = "vpos-closing-overlay";
    overlay.innerHTML = `<div class="vpos-closing-modal" style="text-align:center;padding:36px;color:#c9d1d9;">⏳ Calculating shift sales...</div>`;
    document.body.appendChild(overlay);

    // Always fetch live shift metrics from server
    const shiftRes = await api("vm_pos_get_shift", {
      company: this.company || "ULTRA MRF",
      user: this.cashier || this.user || "Administrator"
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

    // Shift-isolated metrics
    const totalCollected = parseFloat(shift.total_sales || 0);
    const invoiceCount = parseInt(shift.total_invoices || 0);
    const expectedClose = parseFloat(shift.expected_closing || (self.openingAmount + totalCollected));
    const peso = v => "₱ " + parseFloat(v||0).toLocaleString("en-PH", {minimumFractionDigits:2, maximumFractionDigits:2});

    overlay.innerHTML = `<div class="vpos-closing-modal">
      <div class="vpos-closing-title">🔴 Close Shift</div>
      <div class="vpos-closing-sub">End of shift summary for <b>${shift.name}</b></div>

      <div class="vpos-summary-row"><span class="lbl">Opening Cash Float</span><span class="amt">${peso(self.openingAmount)}</span></div>
      <div class="vpos-summary-row"><span class="lbl">Sales in This Shift</span><span class="amt pos">${peso(totalCollected)}</span></div>
      <div class="vpos-summary-row"><span class="lbl">Invoices in Shift</span><span class="amt">${invoiceCount} invoice${invoiceCount === 1 ? '' : 's'}</span></div>
      <div class="vpos-summary-row"><span class="lbl">Expected Cash in Drawer</span><span class="amt" style="font-size:16px;color:#16c784;">${peso(expectedClose)}</span></div>

      <div class="vpos-shift-label" style="margin-top:20px">Actual Cash Count (₱)</div>
      <input class="vpos-shift-input" id="closing-amount" type="number" min="0" step="0.01"
             placeholder="Count your cash drawer and enter total" value="${expectedClose.toFixed(2)}">

      <div id="closing-diff-row" style="margin-top:10px;font-size:13px;font-weight:700;color:#16c784;text-align:right;">
        Difference: <span id="closing-diff-val">₱ 0.00</span>
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
            user: self.cashier || self.user || "Administrator"
          })
        });
        if (result && result.name) {
          overlay.remove();
          alert("✅ Shift Closed Successfully!\\n\\n" +
            "Closing Entry: " + result.name + "\\n" +
            "Invoices in Shift: " + result.total_invoices + "\\n" +
            "Sales in Shift: " + peso(result.grand_total) + "\\n" +
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
    print("3. Injected shift-isolated showCloseShiftModal() into HTML.")
else:
    print("3. Warning: could not locate showCloseShiftModal indices.")

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
