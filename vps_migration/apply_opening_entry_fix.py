"""
Patch current_pos_terminal.html:
1. Add new CSS for .vpos-shift-quick-btn, .vpos-shift-profile-card, .vpos-shift-alert-box
2. Replace buildOpeningEntry with selectable company, strict POS profile validation, required amount float
3. Sync to Web Page/vehicle-pos-terminal and frappe-bench/apps/.../pos_terminal.html
"""
import urllib.request, urllib.parse, json, http.cookiejar, os

PATH = r'c:\Users\josem\erpnext-system\vps_migration\current_pos_terminal.html'
with open(PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add extra CSS if not present
css_anchor = '/* Close-Shift button on nav rail */'
extra_css = """
.vpos-shift-quick-btn {
  background: #21262d; color: #c9d1d9; border: 1px solid #30363d;
  border-radius: 8px; padding: 6px 12px; font-size: 12px; font-weight: 600;
  cursor: pointer; transition: all .15s;
}
.vpos-shift-quick-btn:hover {
  background: #30363d; color: #fff; border-color: #16c784;
}
.vpos-shift-profile-card {
  background: #0d1117; border: 1px solid #30363d; border-radius: 10px;
  padding: 10px 14px; font-size: 13px; color: #f0f6fc; text-align: left;
  display: flex; align-items: center; justify-content: space-between;
}
.vpos-shift-alert-box {
  background: rgba(239, 68, 68, 0.12); border: 1.5px solid #ef4444;
  border-radius: 12px; padding: 12px 14px; color: #fca5a5; font-size: 12.5px;
  line-height: 1.5; text-align: left; margin-top: 10px;
}
"""

if css_anchor in html and '.vpos-shift-quick-btn' not in html:
    html = html.replace(css_anchor, extra_css + '\n' + css_anchor, 1)
    print('Added CSS successfully.')

# 2. Replace buildOpeningEntry(meta)
target_start = '  buildOpeningEntry(meta) {'
target_end = '  async showCloseShiftModal() {'

pos_start = html.find(target_start)
pos_end = html.find(target_end)

if pos_start == -1 or pos_end == -1:
    print('ERROR: Could not locate buildOpeningEntry bounds:', pos_start, pos_end)
    exit(1)

new_build_func = """  buildOpeningEntry(meta) {
    const r = document.getElementById("vpos-root");
    const profiles = (meta && meta.profiles) || [];
    const mops = (meta && meta.modes_of_payment) || [{ name: "Cash", type: "Cash" }];
    const companies = (meta && meta.companies) || [];

    // Pre-select cashier's assigned company or meta default or first available company
    const cashierCompany = this.company || (meta && meta.default_company) || (companies.length ? companies[0] : "");
    const cashierName = this.empName || this.cashier || this.user || "Cashier";
    const cashierDesignation = this.designation || (meta && meta.cashier_details && meta.cashier_details.designation) || "Cashier";
    const cashierEmpNo = this.empNo || (meta && meta.cashier_details && meta.cashier_details.employee) || "—";
    const todayFormatted = new Date().toLocaleDateString("en-PH", { weekday:"long", year:"numeric", month:"long", day:"numeric" });

    const companiesHtml = companies.map(c => `<option value="${c}" ${c === cashierCompany ? "selected" : ""}>${c}</option>`).join("");
    const mopsHtml = mops.map(m => `<option value="${m.name}" ${m.type === "Cash" ? "selected" : ""}>${m.name}</option>`).join("");

    r.innerHTML = `<div class="vpos-shift-screen">
      <div class="vpos-shift-card">
        <div class="vpos-shift-icon">🏪</div>
        <div class="vpos-shift-title">Open Cash Drawer &amp; Shift</div>
        <div class="vpos-shift-sub">Select your company branch and enter opening cash amount</div>

        <div class="vpos-shift-info" style="line-height:1.7;margin-bottom:18px;">
          <div><strong>👤 Cashier:</strong> ${cashierName} <span style="opacity:0.6">(${this.cashier || this.user || ""})</span></div>
          <div><strong>👔 Designation:</strong> ${cashierDesignation} · <strong>Emp #:</strong> ${cashierEmpNo}</div>
          <div><strong>📅 Date:</strong> ${todayFormatted}</div>
        </div>

        <div class="vpos-shift-label">🏢 Company / Branch *</div>
        <select class="vpos-shift-select" id="shift-company">
          ${companiesHtml}
        </select>

        <div class="vpos-shift-label" style="margin-top:16px;">🏪 POS Profile *</div>
        <div id="shift-profile-wrapper"></div>
        <div class="vpos-shift-alert-box" id="shift-profile-err" style="display:none;"></div>

        <div class="vpos-shift-label" style="margin-top:16px;">💵 Opening Cash Amount (₱) *</div>
        <div style="text-align:left;font-size:11px;color:#8b949e;margin-bottom:6px;">* Count your starting cash float in drawer. Required to start shift.</div>
        <input class="vpos-shift-input" id="shift-opening-amount" type="number" min="0" step="0.01" placeholder="0.00" value="0.00">
        
        <div style="display:flex;gap:6px;margin-top:8px;">
          <button type="button" class="vpos-shift-quick-btn" data-add="100">+100</button>
          <button type="button" class="vpos-shift-quick-btn" data-add="200">+200</button>
          <button type="button" class="vpos-shift-quick-btn" data-add="500">+500</button>
          <button type="button" class="vpos-shift-quick-btn" data-add="1000">+1000</button>
          <button type="button" class="vpos-shift-quick-btn" data-clear="true" style="background:#30363d;margin-left:auto;">Clear</button>
        </div>

        <div class="vpos-shift-label" style="margin-top:16px;">Payment Mode</div>
        <select class="vpos-shift-select" id="shift-mop">
          ${mopsHtml}
        </select>

        <button class="vpos-shift-btn" id="shift-open-btn">🟢 Open Shift &amp; Start POS</button>
        <div class="vpos-shift-err" id="shift-err"></div>
      </div>
    </div>`;

    const self = this;
    const compSelect = document.getElementById("shift-company");
    const wrapper = document.getElementById("shift-profile-wrapper");
    const profErr = document.getElementById("shift-profile-err");
    const openBtn = document.getElementById("shift-open-btn");
    const amountInput = document.getElementById("shift-opening-amount");

    // Dynamic resolution of POS Profile when company changes
    const syncProfileForCompany = (selectedCo) => {
      const matched = profiles.filter(p => p.company === selectedCo);
      if (!matched || matched.length === 0) {
        wrapper.innerHTML = `<div style="color:#ef4444;font-size:13px;font-weight:700;padding:8px 0;text-align:left;">❌ No POS Profile registered for ${selectedCo}</div>`;
        profErr.innerHTML = `⚠️ <strong>POS Profile Required:</strong> Company <em>"${selectedCo}"</em> does not have a default POS Profile registered.<br>Please register a POS Profile in ERPNext (<strong>POS Profile &gt; New</strong>) first before opening a shift for this company.`;
        profErr.style.display = "block";
        openBtn.disabled = true;
        openBtn.style.opacity = "0.45";
        openBtn.style.cursor = "not-allowed";
        openBtn.title = "Please register a POS Profile in ERPNext first";
      } else {
        profErr.style.display = "none";
        openBtn.disabled = false;
        openBtn.style.opacity = "1";
        openBtn.style.cursor = "pointer";
        openBtn.title = "";

        if (matched.length === 1) {
          wrapper.innerHTML = `<div class="vpos-shift-profile-card">
            <div>
              <strong style="color:#16c784;">✔ ${matched[0].name}</strong><br>
              <span style="color:#8b949e;font-size:11px;">Warehouse: ${matched[0].warehouse || 'Default'}</span>
            </div>
            <span style="background:rgba(22,199,132,0.15);color:#16c784;padding:3px 8px;border-radius:6px;font-size:10.5px;font-weight:700;">ERPNext Profile</span>
            <input type="hidden" id="shift-profile" value="${matched[0].name}">
          </div>`;
        } else {
          wrapper.innerHTML = `<select class="vpos-shift-select" id="shift-profile">
            ${matched.map(p => `<option value="${p.name}">${p.name} (${p.warehouse || 'Default'})</option>`).join("")}
          </select>`;
        }
      }
    };

    if (compSelect) {
      compSelect.onchange = () => {
        syncProfileForCompany(compSelect.value);
      };
      syncProfileForCompany(compSelect.value);
    }

    // Quick add buttons
    r.querySelectorAll(".vpos-shift-quick-btn").forEach(btn => {
      btn.onclick = () => {
        if (btn.getAttribute("data-clear") === "true") {
          amountInput.value = "0.00";
        } else {
          const addVal = parseFloat(btn.getAttribute("data-add") || 0);
          const curVal = parseFloat(amountInput.value || 0);
          amountInput.value = (curVal + addVal).toFixed(2);
        }
      };
    });

    // Open shift submission
    openBtn.onclick = async () => {
      const errEl = document.getElementById("shift-err");
      errEl.textContent = "";

      const selectedCompany = compSelect ? compSelect.value : "";
      const profInput = document.getElementById("shift-profile");
      const selectedProfile = profInput ? profInput.value : "";
      const openingAmountVal = parseFloat(amountInput.value);

      if (!selectedCompany) {
        errEl.textContent = "Please select a company.";
        return;
      }

      if (!selectedProfile) {
        errEl.textContent = "Cannot open shift: No POS Profile registered for " + selectedCompany + ". Please create one in ERPNext first.";
        return;
      }

      if (isNaN(openingAmountVal) || openingAmountVal < 0) {
        errEl.textContent = "Please enter a valid opening amount (0.00 or greater).";
        amountInput.focus();
        return;
      }

      const mop = document.getElementById("shift-mop").value;

      openBtn.disabled = true;
      openBtn.textContent = "⏳ Opening shift in ERPNext...";

      try {
        const result = await api("vm_pos_open_shift", {
          data: JSON.stringify({
            company: selectedCompany,
            pos_profile: selectedProfile,
            opening_amount: openingAmountVal,
            mode_of_payment: mop,
            user: self.cashier || self.user
          })
        });

        if (result && result.name) {
          self.company = result.company || selectedCompany;
          self.posProfile = result.pos_profile || selectedProfile;
          self.openingEntry = result.name;
          self.openingAmount = parseFloat(result.opening_amount || openingAmountVal);
          self.shiftMop = result.mode_of_payment || mop;
          self.build();
          self.load();
        } else {
          errEl.textContent = "Failed to open shift. Please try again.";
          openBtn.disabled = false;
          openBtn.textContent = "🟢 Open Shift & Start POS";
        }
      } catch(e) {
        errEl.textContent = "Error: " + (e.message || e);
        openBtn.disabled = false;
        openBtn.textContent = "🟢 Open Shift & Start POS";
      }
    };

    amountInput.addEventListener("keydown", e => {
      if (e.key === "Enter") openBtn.click();
    });
  },

"""

html = html[:pos_start] + new_build_func + html[pos_end:]

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(html)
print('Updated current_pos_terminal.html successfully! New length:', len(html))

# Also copy to frappe-bench/.../pos_terminal.html
bench_path = r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\www\pos_terminal.html'
with open(bench_path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Copied to bench pos_terminal.html successfully!')

# Sync to Web Page/vehicle-pos-terminal
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal',
    data=urllib.parse.urlencode({'data': json.dumps({'main_section_html': html})}).encode(),
    headers=H
)
req.get_method = lambda: 'PUT'
res = op.open(req)
print('Synced to live Web Page/vehicle-pos-terminal! Status:', res.status)
