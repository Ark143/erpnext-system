import urllib.request, json, re

with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add CSS for non-pos layout, branch badge, payment buttons, remarks, and hide vpos-idcard
css_patch = """
/* Non-POS full-width layout for History & Profile */
.vpos-app.non-pos {
  grid-template-columns: 68px 1fr !important;
  grid-template-areas: "rail main" !important;
}
.vpos-app.non-pos #vpos-ticket-panel {
  display: none !important;
}
.vpos-view {
  width: 100%;
  min-width: 0;
}
.vpos-idcard {
  display: none !important;
}

/* Branch Locked Badge (No dropdown) */
.vpos-branch-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 46px;
  padding: 0 16px;
  background: #eef7f3;
  border: 1.5px solid #cce8dd;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 700;
  color: var(--txt);
  white-space: nowrap;
}
.vpos-branch-lbl {
  font-size: 11px;
  font-weight: 800;
  color: var(--slate);
  letter-spacing: 0.5px;
}
.vpos-branch-val {
  color: #0fa76d;
  font-weight: 800;
}

/* Payment Method Quick Buttons */
.vpos-pay-methods {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  margin-top: 4px;
}
.vpos-pay-btn {
  height: 38px;
  border: 1.5px solid var(--line);
  background: #fff;
  border-radius: 10px;
  font-family: var(--font-base);
  font-size: 11.5px;
  font-weight: 700;
  color: var(--txt);
  cursor: pointer;
  transition: all .15s;
  touch-action: manipulation;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.vpos-pay-btn:hover {
  border-color: var(--mint);
  background: #f0faf5;
}
.vpos-pay-btn.active {
  background: var(--mint);
  border-color: var(--mint);
  color: #04201a;
  box-shadow: 0 2px 8px rgba(22,199,132,0.3);
}

/* Notes & Remarks input */
.vpos-remarks {
  width: 100%;
  height: 42px;
  border: 1.5px solid var(--line);
  border-radius: 12px;
  padding: 0 14px;
  font-size: 13px;
  font-family: var(--font-base);
  background: #fff;
  outline: none;
  transition: border-color .15s;
}
.vpos-remarks:focus {
  border-color: var(--mint);
}
"""

# Insert css_patch before </style>
html = html.replace('</style>', css_patch + '\n</style>', 1)

# 2. Update navigation rail: remove redundant "ticket" icon
old_nav = """        <div class="vpos-rail-nav">
          <div class="vpos-rail-ic active" data-view="pos" title="Catalog / Point of Sale">&#128722;</div>
          <div class="vpos-rail-ic" data-view="ticket" id="vpos-rail-ticket-btn" title="Cart & Ticket">&#129534;</div>
          <div class="vpos-rail-ic" data-view="history" title="Transaction History">&#128202;</div>
          <div class="vpos-rail-ic" data-view="profile" title="Cashier ID Badge">&#128100;</div>
        </div>"""

new_nav = """        <div class="vpos-rail-nav">
          <div class="vpos-rail-ic active" data-view="pos" title="Point of Sale (Catalog & Ticket)">&#128722;</div>
          <div class="vpos-rail-ic" data-view="history" title="Transaction History">&#128202;</div>
          <div class="vpos-rail-ic" data-view="profile" title="Cashier ID Profile">&#128100;</div>
        </div>"""
html = html.replace(old_nav, new_nav)

# 3. Replace branch dropdown with locked branch badge
old_branch = """            <div class="vpos-branch-row">
              <div class="vpos-branch"><label>Branch</label><select class="vpos-company" disabled></select></div>
              <button class="vpos-stock-toggle" id="vpos-stock-toggle" title="Toggle in-stock filter">In Stock: OFF</button>
            </div>"""

new_branch = """            <div class="vpos-branch-row">
              <div class="vpos-branch-badge" title="Assigned Cashier Branch (Auto-detected from Employee Details)">
                <span class="vpos-branch-lbl">🏢 BRANCH:</span>
                <span class="vpos-branch-val" id="vpos-branch-name">${this.company || "All Branches"}</span>
              </div>
              <button class="vpos-stock-toggle" id="vpos-stock-toggle" title="Toggle in-stock filter">In Stock: OFF</button>
            </div>"""
html = html.replace(old_branch, new_branch)

# 4. In ticket panel, add Payment Method buttons and Notes / Remarks
old_tender = """        <div class="vpos-tender">
          <div class="vpos-tender-row">
            <input class="vpos-paid" type="text" readonly value="0" placeholder="Tap to enter paid amount">
          </div>
          <div class="vpos-quick">
            <button data-q="100">+100</button>
            <button data-q="200">+200</button>
            <button data-q="500">+500</button>
            <button data-q="1000">+1000</button>
          </div>
          <div class="vpos-tot-row vpos-change"><span>Change</span><span class="vpos-balance">₱0.00</span></div>
        </div>"""

new_tender = """        <div class="vpos-field">
          <label>Payment Method</label>
          <div class="vpos-pay-methods" id="vpos-pay-methods">
            <button type="button" class="vpos-pay-btn active" data-pay="Cash">💵 Cash</button>
            <button type="button" class="vpos-pay-btn" data-pay="Card">💳 Card</button>
            <button type="button" class="vpos-pay-btn" data-pay="GCash">📱 GCash</button>
            <button type="button" class="vpos-pay-btn" data-pay="Maya">💳 Maya</button>
            <button type="button" class="vpos-pay-btn" data-pay="BDO">🏦 BDO</button>
            <button type="button" class="vpos-pay-btn" data-pay="Bank Transfer">🏦 Bank Transfer</button>
          </div>
        </div>

        <div class="vpos-field">
          <label>Notes / Remarks</label>
          <input class="vpos-remarks" id="vpos-remarks" placeholder="Add order notes, bay reference, check #..." autocomplete="off">
        </div>

        <div class="vpos-tender">
          <div class="vpos-tender-row">
            <input class="vpos-paid" type="text" readonly value="0" placeholder="Tap to enter paid amount">
          </div>
          <div class="vpos-quick">
            <button data-q="100">+100</button>
            <button data-q="200">+200</button>
            <button data-q="500">+500</button>
            <button data-q="1000">+1000</button>
          </div>
          <div class="vpos-tot-row vpos-change"><span>Change</span><span class="vpos-balance">₱0.00</span></div>
        </div>"""
html = html.replace(old_tender, new_tender)

# 5. Update build() logic: remove comp listener, add payment button listener, update switchView
old_comp_binding = """    const comp = r.querySelector(".vpos-company");
    comp.disabled = false;
    comp.value = this.company || "";
    comp.onchange = () => { this.company = comp.value || null; this.totals(); this.search(); };"""

new_comp_binding = """    // Auto-selected branch (no dropdown)
    const bVal = r.querySelector("#vpos-branch-name");
    if (bVal) bVal.textContent = this.company || "All Branches";

    // Payment method quick buttons
    this.payment_method = "Cash";
    r.querySelectorAll(".vpos-pay-btn").forEach(btn => {
      btn.onclick = () => {
        r.querySelectorAll(".vpos-pay-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        self.payment_method = btn.getAttribute("data-pay");
        if (self.payment_method !== "Cash") {
          const tot = self.total || 0;
          const pInput = document.querySelector(".vpos-paid");
          if (pInput && (flt(pInput.value) <= 0 || flt(pInput.value) < tot)) {
            pInput.value = tot;
            self.totals();
          }
        }
      };
    });"""
html = html.replace(old_comp_binding, new_comp_binding)

# 6. Update load() logic so it does not overwrite company with dropdown options
old_load_comp = """    // Populate the Company (Branch) select so Charge & Pay can enable even if
    // the cashier profile returned no company. Default to cashier company or
    // the first available company.
    const comp = document.querySelector(".vpos-company");
    if (meta && comp) {
      const companies = meta.companies || [];
      comp.innerHTML = "";
      companies.forEach(c => {
        const o = document.createElement("option");
        o.value = c; o.textContent = c;
        comp.appendChild(o);
      });
      if (!this.company && companies.length) this.company = companies[0];
      comp.value = this.company || "";
    }"""

new_load_comp = """    // Ensure company is set from cashier employee record or first meta company
    if (!this.company && meta && meta.companies && meta.companies.length) {
      this.company = meta.companies[0];
    }
    const bName = document.getElementById("vpos-branch-name");
    if (bName) bName.textContent = this.company || "All Branches";
    const coFoot = document.getElementById("vpos-co");
    if (coFoot) coFoot.innerHTML = (this.company || "") + "<br>" + (this.cashier || "");"""
html = html.replace(old_load_comp, new_load_comp)

# 7. Update switchView(v) to eliminate overlapping:
# Hide ticket panel and adjust grid to 2 columns on non-pos views
old_switch_view = """  switchView(v) {
    document.querySelectorAll(".vpos-rail-ic").forEach(x => x.classList.toggle("active", x.getAttribute("data-view") === v));
    const map = { pos: "vpos-view-pos", history: "vpos-view-history", profile: "vpos-view-profile" };
    
    if (v === "ticket") {
      this.toggleMobileTicket(true);
      return;
    } else {
      this.toggleMobileTicket(false);
    }

    Object.keys(map).forEach(k => {
      const el = document.getElementById(map[k]);
      if (el) el.style.display = (k === v ? "block" : "none");
    });

    if (v === "pos") { this.renderPOS(); }
    else if (v === "history") { this.renderHistory(); }
    else if (v === "profile") { this.renderProfile(); }
  },"""

new_switch_view = """  switchView(v) {
    document.querySelectorAll(".vpos-rail-ic").forEach(x => x.classList.toggle("active", x.getAttribute("data-view") === v));
    const app = document.querySelector(".vpos-app");
    const ticketPanel = document.getElementById("vpos-ticket-panel");

    if (v === "pos") {
      if (app) app.classList.remove("non-pos");
      if (ticketPanel) ticketPanel.style.display = "";
    } else {
      if (app) app.classList.add("non-pos");
      if (ticketPanel) ticketPanel.style.display = "none";
    }

    const map = { pos: "vpos-view-pos", history: "vpos-view-history", profile: "vpos-view-profile" };
    Object.keys(map).forEach(k => {
      const el = document.getElementById(map[k]);
      if (el) el.style.display = (k === v ? "block" : "none");
    });

    if (v === "pos") { this.renderPOS(); }
    else if (v === "history") { this.renderHistory(); }
    else if (v === "profile") { this.renderProfile(); }
  },"""
html = html.replace(old_switch_view, new_switch_view)

# 8. Update renderProfile() to show ONLY ID Profile Details (no unstyled duplicate card below)
old_render_profile = """    view.innerHTML = `
    <div class="vpos-prof">
      <div class="vpos-prof-card" id="vpos-prof-card">
        <div class="vpos-prof-logo">V</div>
        <h3>Cashier ID Badge</h3>
        <div class="vpos-prof-row"><span>Employee #</span><b>${this.empNo || "—"}</b></div>
        <div class="vpos-prof-row"><span>Employee</span><b>${this.empName || this.employee || "—"}</b></div>
        <div class="vpos-prof-row"><span>Designation</span><b>${this.designation || "—"}</b></div>
        <div class="vpos-prof-row"><span>Company</span><b>${this.company || ""}</b></div>
        <div class="vpos-prof-row"><span>Branch</span><b>${this.branch || "—"}</b></div>
        <div class="vpos-prof-row"><span>Department</span><b>${this.department || "—"}</b></div>
        <div class="vpos-prof-row"><span>Reports To</span><b>${this.reportsTo || "—"}</b></div>
        <div class="vpos-prof-row"><span>Email</span><b>${this.email || this.cashier || ""}</b></div>
        <div class="vpos-prof-qr">${svg}</div>
        <div class="vpos-prof-hint">Scan badge with any camera to log in instantly.</div>
        <div class="vpos-prof-code" id="vpos-prof-code">${qrData}</div>
        <button class="vpos-li-qr" id="vpos-prof-dl" style="margin-top:12px">&#11015; Download Badge (SVG)</button>
        <button class="vpos-li-qr" id="vpos-prof-copy" style="margin-top:8px">&#128203; Copy Badge Code</button>
      </div>
      <button class="vpos-prof-print" onclick="window.print()">&#128424; Print Badge</button>
    </div>
    <div class="vpos-idcard" id="vpos-idcard">
      <div class="vpos-id-head">
        <div class="vpos-id-logo">V</div>
        <div class="vpos-id-co">${this.company || ""}</div>
        <div class="vpos-id-title">CASHIER ID</div>
      </div>
      <div class="vpos-id-body">
        <div class="vpos-id-info">
          <div class="vpos-id-name">${this.empName || this.employee || "—"}</div>
          <div class="vpos-id-line"><span>Emp #</span><b>${this.empNo || "—"}</b></div>
          <div class="vpos-id-line"><span>Designation</span><b>${this.designation || "—"}</b></div>
          <div class="vpos-id-line"><span>Branch</span><b>${this.branch || "—"}</b></div>
          <div class="vpos-id-line"><span>Email</span><b>${this.email || this.cashier || ""}</b></div>
        </div>
        <div class="vpos-id-qr">${svg}</div>
      </div>
    </div>`;"""

new_render_profile = """    view.innerHTML = `
    <div class="vpos-prof">
      <div class="vpos-prof-card" id="vpos-prof-card">
        <div class="vpos-prof-logo">V</div>
        <h3 style="margin:2px 0 4px">Official Cashier ID Profile</h3>
        <div style="font-size:11.5px;color:var(--muted);margin-bottom:14px;font-weight:700;letter-spacing:0.5px">ULTRA MRF AUTHORIZED PERSONNEL</div>
        <div class="vpos-prof-row"><span>Employee Name</span><b>${this.empName || this.employee || "—"}</b></div>
        <div class="vpos-prof-row"><span>Employee #</span><b>${this.empNo || "—"}</b></div>
        <div class="vpos-prof-row"><span>Designation</span><b>${this.designation || "Cashier"}</b></div>
        <div class="vpos-prof-row"><span>Assigned Company</span><b>${this.company || "—"}</b></div>
        <div class="vpos-prof-row"><span>Branch</span><b>${this.branch || "—"}</b></div>
        <div class="vpos-prof-row"><span>Department</span><b>${this.department || "Front Desk"}</b></div>
        <div class="vpos-prof-row"><span>Reports To</span><b>${this.reportsTo || "—"}</b></div>
        <div class="vpos-prof-row"><span>User Account</span><b>${this.email || this.cashier || ""}</b></div>
        <div class="vpos-prof-qr">${svg}</div>
        <div class="vpos-prof-hint">Scan badge with device camera for instant shift sign-in and warehouse material handover verification.</div>
        <div class="vpos-prof-code" id="vpos-prof-code">${qrData}</div>
        <div style="display:flex;gap:8px;margin-top:14px;width:100%">
          <button class="vpos-li-qr" id="vpos-prof-dl" style="flex:1">&#11015; Download SVG</button>
          <button class="vpos-li-qr" id="vpos-prof-copy" style="flex:1">&#128203; Copy Code</button>
          <button class="vpos-prof-print" onclick="window.print()" style="flex:1;padding:10px 14px">&#128424; Print Badge</button>
        </div>
      </div>
    </div>`;"""
html = html.replace(old_render_profile, new_render_profile)

# 9. Update clear() to reset remarks and payment method
old_clear = """  clear() {
    this.cart = []; this.customer = null; this.vehicle = null;
    const cEl = document.querySelector(".vpos-cust"); if (cEl) cEl.textContent = "";
    const vEl = document.querySelector(".vpos-vin"); if (vEl) vEl.value = "";
    const pEl = document.querySelector(".vpos-paid"); if (pEl) pEl.value = 0;
    this.totals();
    this.cartRender();
    this.search();
    this.toggleMobileTicket(false);
  },"""

new_clear = """  clear() {
    this.cart = []; this.customer = null; this.vehicle = null;
    this.payment_method = "Cash";
    document.querySelectorAll(".vpos-pay-btn").forEach(b => b.classList.toggle("active", b.getAttribute("data-pay") === "Cash"));
    const remEl = document.getElementById("vpos-remarks"); if (remEl) remEl.value = "";
    const cEl = document.querySelector(".vpos-cust"); if (cEl) cEl.textContent = "";
    const vEl = document.querySelector(".vpos-vin"); if (vEl) vEl.value = "";
    const pEl = document.querySelector(".vpos-paid"); if (pEl) pEl.value = 0;
    this.totals();
    this.cartRender();
    this.search();
    this.toggleMobileTicket(false);
  },"""
html = html.replace(old_clear, new_clear)

# 10. Update submit() to send remarks
old_submit = """  async submit(tot, paid) {
    const items = this.cart.map(c => ({ item_code: c.item_code, qty: c.qty, rate: c.rate, discount_amount: c.discount_amount, uom: c.uom }));
    const r = await api("vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice.create_from_pos", {
      data: JSON.stringify({ customer: this.customer, vehicle: this.vehicle || null, company: this.company, paid_amount: paid, payment_method: this.payment_method, items: items })
    });"""

new_submit = """  async submit(tot, paid) {
    const items = this.cart.map(c => ({ item_code: c.item_code, qty: c.qty, rate: c.rate, discount_amount: c.discount_amount, uom: c.uom }));
    const remEl = document.getElementById("vpos-remarks");
    const remarks = remEl ? remEl.value.trim() : "";
    const r = await api("vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice.create_from_pos", {
      data: JSON.stringify({
        customer: this.customer,
        vehicle: this.vehicle || null,
        company: this.company,
        paid_amount: paid,
        payment_method: this.payment_method || "Cash",
        remarks: remarks,
        items: items
      })
    });"""
html = html.replace(old_submit, new_submit)

# Write to local patched files
with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated local files. Now saving to live ERPNext Web Page 'vehicle-pos-terminal'...")

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

save_url = 'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal'
payload = json.dumps({'main_section_html': html}).encode('utf-8')
req = urllib.request.Request(save_url, data=payload, headers={'Content-Type': 'application/json'}, method='PUT')
res = opener.open(req)
print("SUCCESSFULLY updated Web Page vehicle-pos-terminal! Status:", res.status)
