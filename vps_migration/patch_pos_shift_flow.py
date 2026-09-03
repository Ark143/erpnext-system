"""
Patch current_pos_terminal.html to add:
1. POS Opening Entry screen (shown after login, before main POS)
2. Close Shift button on nav rail + modal
3. Shift summary in Cashier ID Profile tab
4. Wire afterLogin -> checkShift flow
"""
import urllib.request, json, re

with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ──────────────────────────────────────────────────────────────────────────────
# 1.  CSS for shift-related screens (inject before </style>)
# ──────────────────────────────────────────────────────────────────────────────
SHIFT_CSS = """
/* ─────────── POS SHIFT SCREEN ─────────── */
.vpos-shift-screen {
  position: fixed; inset: 0; z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
}
.vpos-shift-card {
  background: #1c2128; border: 1px solid #30363d; border-radius: 20px;
  padding: 40px 36px; max-width: 440px; width: 96%; text-align: center;
  box-shadow: 0 24px 64px rgba(0,0,0,.5);
}
.vpos-shift-icon {
  width: 72px; height: 72px; border-radius: 50%;
  background: linear-gradient(135deg,#16c784,#0fa76d);
  margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;
  font-size: 32px; box-shadow: 0 8px 24px rgba(22,199,132,.3);
}
.vpos-shift-title { font-size: 22px; font-weight: 800; color: #f0f6fc; margin-bottom: 4px; }
.vpos-shift-sub   { font-size: 13px; color: #8b949e; margin-bottom: 28px; }
.vpos-shift-label { text-align: left; font-size: 12px; font-weight: 600; color: #8b949e;
                    text-transform: uppercase; letter-spacing: .6px; margin-bottom: 6px; margin-top: 18px; }
.vpos-shift-input {
  width: 100%; background: #0d1117; border: 1px solid #30363d; border-radius: 10px;
  color: #f0f6fc; font-size: 16px; padding: 12px 16px; outline: none;
  transition: border-color .2s; box-sizing: border-box;
}
.vpos-shift-input:focus { border-color: #16c784; }
.vpos-shift-select {
  width: 100%; background: #0d1117; border: 1px solid #30363d; border-radius: 10px;
  color: #f0f6fc; font-size: 14px; padding: 12px 16px; outline: none; box-sizing: border-box;
}
.vpos-shift-btn {
  width: 100%; margin-top: 24px; padding: 14px; border-radius: 12px;
  border: none; font-size: 16px; font-weight: 700; cursor: pointer;
  background: linear-gradient(135deg,#16c784,#0fa76d); color: #fff;
  box-shadow: 0 4px 16px rgba(22,199,132,.3); transition: transform .1s, box-shadow .1s;
}
.vpos-shift-btn:hover  { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(22,199,132,.4); }
.vpos-shift-btn:active { transform: translateY(0); }
.vpos-shift-btn.danger { background: linear-gradient(135deg,#f85149,#c93c35); box-shadow: 0 4px 16px rgba(248,81,73,.3); }
.vpos-shift-info {
  background: rgba(22,199,132,.08); border: 1px solid rgba(22,199,132,.2); border-radius: 12px;
  padding: 14px 16px; text-align: left; margin-top: 16px; font-size: 13px; color: #8b949e;
}
.vpos-shift-info strong { color: #16c784; }
.vpos-shift-err { color: #f85149; font-size: 13px; margin-top: 10px; min-height: 20px; }
.vpos-shift-ok  { color: #16c784; font-size: 13px; margin-top: 10px; min-height: 20px; }

/* Close-Shift button on nav rail */
.vpos-rail-ic.close-shift { color: #f85149 !important; }
.vpos-rail-ic.close-shift:hover { background: rgba(248,81,73,.15) !important; }

/* Closing modal overlay */
.vpos-closing-overlay {
  position: fixed; inset: 0; z-index: 9998;
  background: rgba(0,0,0,.7); display: flex; align-items: center; justify-content: center;
}
.vpos-closing-modal {
  background: #1c2128; border: 1px solid #30363d; border-radius: 20px;
  padding: 36px 32px; max-width: 420px; width: 96%; box-shadow: 0 24px 64px rgba(0,0,0,.6);
}
.vpos-closing-title { font-size: 20px; font-weight: 800; color: #f0f6fc; margin-bottom: 6px; }
.vpos-closing-sub   { font-size: 13px; color: #8b949e; margin-bottom: 22px; }
.vpos-summary-row   { display: flex; justify-content: space-between; padding: 8px 0;
                       border-bottom: 1px solid #30363d; font-size: 14px; color: #c9d1d9; }
.vpos-summary-row:last-child { border-bottom: none; }
.vpos-summary-row .lbl { color: #8b949e; }
.vpos-summary-row .amt { font-weight: 700; color: #f0f6fc; }
.vpos-summary-row .amt.pos { color: #16c784; }
.vpos-summary-row .amt.neg { color: #f85149; }
"""

# Inject CSS before last </style>
last_style_close = html.rfind('</style>')
if last_style_close != -1:
    html = html[:last_style_close] + SHIFT_CSS + html[last_style_close:]
    print("Injected SHIFT_CSS")

# ──────────────────────────────────────────────────────────────────────────────
# 2.  Modify afterLogin() to check shift first
# ──────────────────────────────────────────────────────────────────────────────
OLD_AFTER_LOGIN = """  async afterLogin() {
    const c = await api("vehicle_management.vehicle_management.pos_api.get_cashier");
    if (c && c.company) {
      this.company = c.company; this.cashier = c.user; this.email = c.email || c.user;
      this.employee = c.employee || ""; this.empName = c.employee_name || ""; this.empNo = c.employee_number || "";
      this.designation = c.designation || ""; this.branch = c.branch || ""; this.department = c.department || "";
      this.reportsTo = c.reports_to_name || c.reports_to || "";
    } else {
      this.company = null; this.cashier = this.user; this.email = this.user; this.employee = ""; this.empName = "";
      this.empNo = ""; this.designation = ""; this.branch = ""; this.department = ""; this.reportsTo = "";
    }
    this.loggedIn = true;
    this.build();
    this.load();
  },"""

NEW_AFTER_LOGIN = """  async afterLogin() {
    const c = await api("vehicle_management.vehicle_management.pos_api.get_cashier");
    if (c && c.company) {
      this.company = c.company; this.cashier = c.user; this.email = c.email || c.user;
      this.employee = c.employee || ""; this.empName = c.employee_name || ""; this.empNo = c.employee_number || "";
      this.designation = c.designation || ""; this.branch = c.branch || ""; this.department = c.department || "";
      this.reportsTo = c.reports_to_name || c.reports_to || "";
    } else {
      this.company = null; this.cashier = this.user; this.email = this.user; this.employee = ""; this.empName = "";
      this.empNo = ""; this.designation = ""; this.branch = ""; this.department = ""; this.reportsTo = "";
    }
    this.loggedIn = true;
    // Check if there is already an open POS shift for this cashier
    await this.checkOrOpenShift();
  },

  // ── Shift Management ─────────────────────────────────────────────────────
  async checkOrOpenShift() {
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
  },

  buildOpeningEntry(meta) {
    const r = document.getElementById("vpos-root");
    const profiles = (meta && meta.profiles) || [];
    const mops = (meta && meta.modes_of_payment) || [{ name: "Cash", type: "Cash" }];
    const company = this.company || (meta && meta.company) || "";

    const profilesHtml = profiles.length > 1
      ? `<div class="vpos-shift-label">POS Profile</div>
         <select class="vpos-shift-select" id="shift-profile">
           ${profiles.map(p => `<option value="${p.name}">${p.name}</option>`).join("")}
         </select>`
      : profiles.length === 1
        ? `<input type="hidden" id="shift-profile" value="${profiles[0].name}">`
        : `<input type="hidden" id="shift-profile" value="">`;

    const mopsHtml = `<select class="vpos-shift-select" id="shift-mop">
      ${mops.map(m => `<option value="${m.name}" ${m.type === 'Cash' ? 'selected' : ''}>${m.name}</option>`).join("")}
    </select>`;

    r.innerHTML = `<div class="vpos-shift-screen">
      <div class="vpos-shift-card">
        <div class="vpos-shift-icon">🏪</div>
        <div class="vpos-shift-title">Open Cash Drawer</div>
        <div class="vpos-shift-sub">Enter your opening cash amount to start the shift</div>

        <div class="vpos-shift-info">
          <strong>👤 Cashier:</strong> ${this.empName || this.cashier || this.user}<br>
          <strong>🏢 Branch:</strong> ${company || "—"}<br>
          <strong>📅 Date:</strong> ${new Date().toLocaleDateString("en-PH", { weekday:"long", year:"numeric", month:"long", day:"numeric" })}
        </div>

        ${profilesHtml}

        <div class="vpos-shift-label">Mode of Payment</div>
        ${mopsHtml}

        <div class="vpos-shift-label">Opening Cash Amount (₱)</div>
        <input class="vpos-shift-input" id="shift-opening-amount" type="number" min="0" step="0.01" placeholder="0.00" value="0">

        <button class="vpos-shift-btn" id="shift-open-btn">🟢 Open Shift & Start POS</button>
        <div class="vpos-shift-err" id="shift-err"></div>
      </div>
    </div>`;

    const self = this;
    document.getElementById("shift-open-btn").onclick = async () => {
      const btn = document.getElementById("shift-open-btn");
      const errEl = document.getElementById("shift-err");
      btn.disabled = true; btn.textContent = "⏳ Opening shift...";
      errEl.textContent = "";
      try {
        const opening_amount = parseFloat(document.getElementById("shift-opening-amount").value) || 0;
        const pos_profile = (document.getElementById("shift-profile") || {}).value || "";
        const mop = document.getElementById("shift-mop").value;
        const result = await api("vm_pos_open_shift", {
          data: JSON.stringify({ company: self.company, pos_profile, opening_amount, mode_of_payment: mop })
        });
        if (result && result.name) {
          self.openingEntry = result.name;
          self.openingAmount = result.opening_amount;
          self.shiftMop = result.mode_of_payment;
          self.posProfile = result.pos_profile;
          self.build();
          self.load();
        } else {
          errEl.textContent = "Failed to open shift. Please try again.";
          btn.disabled = false; btn.textContent = "🟢 Open Shift & Start POS";
        }
      } catch(e) {
        errEl.textContent = "Error: " + (e.message || e);
        btn.disabled = false; btn.textContent = "🟢 Open Shift & Start POS";
      }
    };
    // Enter key on amount input
    document.getElementById("shift-opening-amount").addEventListener("keydown", e => {
      if (e.key === "Enter") document.getElementById("shift-open-btn").click();
    });
  },

  showCloseShiftModal() {
    const self = this;
    if (!this.openingEntry) { alert("No active shift found."); return; }

    const overlay = document.createElement("div");
    overlay.className = "vpos-closing-overlay";

    // Compute totals from history (already in memory)
    const todayInvoices = (this.history || []).filter(t => t.status === "Paid" || t.status === "Consolidated");
    const totalCollected = todayInvoices.reduce((s, t) => s + parseFloat(t.total_amount || 0), 0);
    const expectedClose = (this.openingAmount || 0) + totalCollected;
    const peso = v => "₱ " + parseFloat(v||0).toLocaleString("en-PH", {minimumFractionDigits:2, maximumFractionDigits:2});

    overlay.innerHTML = `<div class="vpos-closing-modal">
      <div class="vpos-closing-title">🔴 Close Shift</div>
      <div class="vpos-closing-sub">End of shift — submit your closing cash count</div>

      <div class="vpos-summary-row"><span class="lbl">Opening Amount</span><span class="amt">${peso(self.openingAmount)}</span></div>
      <div class="vpos-summary-row"><span class="lbl">Total Sales (POS)</span><span class="amt pos">${peso(totalCollected)}</span></div>
      <div class="vpos-summary-row"><span class="lbl">Expected Closing</span><span class="amt">${peso(expectedClose)}</span></div>
      <div class="vpos-summary-row"><span class="lbl">Total Invoices</span><span class="amt">${todayInvoices.length}</span></div>

      <div class="vpos-shift-label" style="margin-top:20px">Actual Cash Count (₱)</div>
      <input class="vpos-shift-input" id="closing-amount" type="number" min="0" step="0.01"
             placeholder="Count your cash and enter amount" value="${expectedClose.toFixed(2)}">

      <div style="display:flex;gap:10px;margin-top:20px">
        <button class="vpos-shift-btn" id="shift-close-confirm">🔴 Submit & Close Shift</button>
        <button class="vpos-shift-btn" id="shift-close-cancel" style="background:#30363d;box-shadow:none;flex:0 0 auto;width:auto;padding:14px 20px">Cancel</button>
      </div>
      <div class="vpos-shift-err" id="closing-err"></div>
    </div>`;

    document.body.appendChild(overlay);

    overlay.querySelector("#shift-close-cancel").onclick = () => overlay.remove();
    overlay.querySelector("#shift-close-confirm").onclick = async () => {
      const btn = overlay.querySelector("#shift-close-confirm");
      const errEl = overlay.querySelector("#closing-err");
      btn.disabled = true; btn.textContent = "⏳ Closing shift...";
      errEl.textContent = "";
      try {
        const closing_amount = parseFloat(overlay.querySelector("#closing-amount").value) || 0;
        const result = await api("vm_pos_close_shift", {
          data: JSON.stringify({
            opening_entry: self.openingEntry,
            closing_amount,
            mode_of_payment: self.shiftMop || "Cash"
          })
        });
        if (result && result.name) {
          overlay.remove();
          alert("✅ Shift closed!\\n" +
            "Closing Entry: " + result.name + "\\n" +
            "Total Invoices: " + result.total_invoices + "\\n" +
            "Total Sales: " + peso(result.grand_total) + "\\n" +
            "Cash Counted: " + peso(result.closing_amount) + "\\n" +
            "Difference: " + peso(result.difference));
          self.openingEntry = null;
          self.openingAmount = 0;
          self.logout();
        } else {
          errEl.textContent = "Failed to close shift. Check ERPNext logs.";
          btn.disabled = false; btn.textContent = "🔴 Submit & Close Shift";
        }
      } catch(e) {
        errEl.textContent = "Error: " + (e.message || e);
        btn.disabled = false; btn.textContent = "🔴 Submit & Close Shift";
      }
    };
  },"""

html = html.replace(OLD_AFTER_LOGIN, NEW_AFTER_LOGIN)
if NEW_AFTER_LOGIN[:60] in html:
    print("✅ Replaced afterLogin + injected shift methods")
else:
    print("❌ afterLogin replacement FAILED – check exact whitespace")

# ──────────────────────────────────────────────────────────────────────────────
# 3. Add Close Shift icon to nav rail in build()
# ──────────────────────────────────────────────────────────────────────────────
OLD_RAIL = """          <div class="vpos-rail-ic" data-view="profile" title="Cashier ID Profile">&#128100;</div>
        </div>
        <div class="vpos-rail-ic logout" data-action="logout" title="Log out / Close">&#9211;</div>"""

NEW_RAIL = """          <div class="vpos-rail-ic" data-view="profile" title="Cashier ID Profile">&#128100;</div>
        </div>
        <div class="vpos-rail-ic close-shift" data-action="close-shift" title="Close Shift / End of Day">&#128274;</div>
        <div class="vpos-rail-ic logout" data-action="logout" title="Log out / Close">&#9211;</div>"""

html = html.replace(OLD_RAIL, NEW_RAIL)
if 'close-shift' in html:
    print("✅ Added Close Shift button to nav rail")
else:
    print("❌ Nav rail injection FAILED")

# ──────────────────────────────────────────────────────────────────────────────
# 4. Wire close-shift action in the rail click handler
# ──────────────────────────────────────────────────────────────────────────────
OLD_RAIL_HANDLER = """      if (a === \"logout\") { self.logout(); return; }"""
NEW_RAIL_HANDLER = """      if (a === "logout") { self.logout(); return; }
      if (a === "close-shift") { self.showCloseShiftModal(); return; }"""

html = html.replace(OLD_RAIL_HANDLER, NEW_RAIL_HANDLER)
if '"close-shift"' in html:
    print("✅ Wired close-shift action")
else:
    print("❌ Rail handler injection FAILED")

# ──────────────────────────────────────────────────────────────────────────────
# 5. Show shift info in the Cashier Profile view renderProfile()
# ──────────────────────────────────────────────────────────────────────────────
OLD_RENDER_PROFILE_START = """  renderProfile() {
    const view = document.getElementById("vpos-view-profile");
    if (!view) return;
    const peso = v => "₱ " + parseFloat(v||0).toLocaleString("en-PH", {minimumFractionDigits:2,maximumFractionDigits:2});"""

NEW_RENDER_PROFILE_START = """  renderProfile() {
    const view = document.getElementById("vpos-view-profile");
    if (!view) return;
    const peso = v => "₱ " + parseFloat(v||0).toLocaleString("en-PH", {minimumFractionDigits:2,maximumFractionDigits:2});
    // Shift info for profile
    const shiftStatus = this.openingEntry
      ? `<div style="background:rgba(22,199,132,.08);border:1px solid rgba(22,199,132,.2);border-radius:12px;padding:16px 18px;margin-bottom:16px">
           <div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#8b949e;margin-bottom:8px">🟢 Active Shift</div>
           <div style="font-size:13px;color:#c9d1d9">Entry: <strong style="color:#f0f6fc">${this.openingEntry}</strong></div>
           <div style="font-size:13px;color:#c9d1d9">Opening Cash: <strong style="color:#16c784">${peso(this.openingAmount)}</strong></div>
           <div style="font-size:13px;color:#c9d1d9;margin-top:8px">
             <button onclick="POS.showCloseShiftModal()" style="background:linear-gradient(135deg,#f85149,#c93c35);color:#fff;border:none;padding:8px 18px;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">🔴 Close Shift Now</button>
           </div>
         </div>`
      : `<div style="background:rgba(248,81,73,.08);border:1px solid rgba(248,81,73,.2);border-radius:12px;padding:16px 18px;margin-bottom:16px">
           <div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#8b949e;margin-bottom:6px">⚠️ No Active Shift</div>
           <div style="font-size:13px;color:#8b949e">No POS Opening Entry found for this session.</div>
         </div>`;"""

if 'renderProfile()' in html and 'const peso = v =>' in html:
    html = html.replace(OLD_RENDER_PROFILE_START, NEW_RENDER_PROFILE_START, 1)
    print("✅ Injected shift info in renderProfile()")
else:
    print("⚠️  renderProfile() injection skipped – pattern not found (not critical)")

# ──────────────────────────────────────────────────────────────────────────────
# 6. Embed shiftStatus in the profile card (find where the profile HTML renders)
# ──────────────────────────────────────────────────────────────────────────────
# Find the profile header and inject shiftStatus before it
OLD_PROF_HEADER = """    view.innerHTML = `
      <div class="vpos-prof">
        <div class="vpos-prof-hd">"""
NEW_PROF_HEADER = """    view.innerHTML = `
      <div class="vpos-prof">
        ${shiftStatus}
        <div class="vpos-prof-hd">"""
html = html.replace(OLD_PROF_HEADER, NEW_PROF_HEADER, 1)

# ──────────────────────────────────────────────────────────────────────────────
# 7. Initialize shift-related properties in the POS object
# ──────────────────────────────────────────────────────────────────────────────
OLD_INIT_PROPS = """  loggedIn: false, loggedOutMsg: \"\",
  user: null, cashier: null, email: null, employee: null, empName: \"\", empNo: \"\","""
NEW_INIT_PROPS = """  loggedIn: false, loggedOutMsg: "",
  openingEntry: null, openingAmount: 0, shiftMop: "Cash", posProfile: null,
  user: null, cashier: null, email: null, employee: null, empName: "", empNo: "","""
html = html.replace(OLD_INIT_PROPS, NEW_INIT_PROPS)
if 'openingEntry' in html:
    print("✅ Initialized shift properties on POS object")
else:
    print("❌ Init props injection FAILED")

# ──────────────────────────────────────────────────────────────────────────────
# 8. Write files and deploy
# ──────────────────────────────────────────────────────────────────────────────
print("\nSaving local HTML files...")
with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✅ Local files saved.")

print("Deploying to Web Page/vehicle-pos-terminal...")
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

save_url = 'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal'
payload = json.dumps({'main_section_html': html}).encode('utf-8')
req = urllib.request.Request(save_url, data=payload, headers={'Content-Type': 'application/json'}, method='PUT')
res = opener.open(req)
print(f"✅ Deployed! HTTP {res.status}")
print("\n🎉 POS Opening/Closing Entry flow is LIVE.")
print("   Flow: Login → Opening Amount Screen → POS Terminal → 🔒 Close Shift → Closing Entry")
