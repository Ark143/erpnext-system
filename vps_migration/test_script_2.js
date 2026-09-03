
var PESO = "\u20B1";
function flt(v) { return Number(v || 0); }
function peso(n) { return PESO + Number(n || 0).toLocaleString("en-US", { minimumFractionDigits: 2 }); }
function esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }

async function api(method, params) {
  let url = "/api/method/" + method;
  const p = Object.assign({}, params || {}, { _: Date.now() });
  const qs = Object.keys(p).map(k => encodeURIComponent(k) + "=" + encodeURIComponent(p[k] == null ? "" : p[k])).join("&");
  if (qs) url += "?" + qs;
  try {
    const r = await fetch(url, {
      cache: "no-store",
      headers: { "X-Requested-With": "XMLHttpRequest" }
    });
    const j = await r.json();
    if (!r.ok) {
      console.error("API error", method, j);
      let errMsg = j.exception || j.exc || "Server error (" + r.status + ")";
      if (j._server_messages) {
        try {
          const msgs = JSON.parse(j._server_messages);
          const parsed = msgs.map(m => typeof m === "string" ? (JSON.parse(m).message || m) : (m.message || m)).join("\n");
          if (parsed) errMsg = parsed;
        } catch(ex) {}
      }
      api.lastError = errMsg;
      return null;
    }
    api.lastError = null;
    return j.message;
  } catch (e) {
    console.error("api", method, e);
    api.lastError = e.message || String(e);
    return null;
  }
}

async function frappeLogin(usr, pwd) {
  const fd = new URLSearchParams();
  fd.set("usr", usr);
  fd.set("pwd", pwd);
  const r = await fetch("/api/method/login", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded", "Expect": "" }, body: fd.toString() });
  const j = await r.json();
  return j;
}

var POS = {
  cart: [], customer: null, vehicle: null, company: null, payment_method: "Cash", category: null, total: 0, _vt: null,
  PROD_LIMIT: 12, showAll: false, STOCK: {}, onlyStock: false, loggedIn: false, user: null, cashier: null,
  history: [], discount: 0, loggedOutMsg: null, mobileTicketOpen: false,

  async init() {
    this.hideChrome();
    this.initTip();
    try {
      const u = await api("frappe.auth.get_logged_user");
      if (u && u !== "Guest") {
        this.user = u;
        await this.afterLogin();
        return;
      }
    } catch (e) {
      console.warn("Session check fallback to login:", e);
    }
    this.buildLogin();
  },

  hideChrome() {
    const hide = () => {
      const nv = document.querySelector("nav.navbar, header.navbar"); if (nv) nv.style.display = "none";
      const wf = document.querySelector("footer.web-footer"); if (wf) wf.style.display = "none";
      const fc = document.querySelector(".page_content"); if (fc) fc.style.padding = "0";
      document.body.style.margin = "0";
    };
    hide();
    window.addEventListener("load", hide);
    setTimeout(hide, 400);
  },

  logout() {
    try { fetch("/api/method/logout", { method: "POST", headers: { "X-Requested-With": "XMLHttpRequest" } }); } catch (e) {}
    window._vposPwd = null;
    this.loggedIn = false; this.cart = []; this.customer = null; this.vehicle = null; this.company = null;
    this.cashier = null; this.email = null; this.employee = null; this.loggedOutMsg = "You have been logged out. Sign in again to continue.";
    this.buildLogin();
  },

  buildLogin() {
    const r = document.getElementById("vpos-root");
    r.innerHTML = `
    <div class="vpos-login" id="vpos-login">
      <div class="vpos-login-card">
        <div class="vpos-login-logo" style="background:linear-gradient(135deg,#16c784,#0fa76d);font-size:22px;font-weight:900;letter-spacing:-1px">V</div>
        <div class="vpos-login-title">Vehicle POS Terminal</div>
        <div class="vpos-login-sub">Cashier Sign-In</div>
        ${this.loggedOutMsg ? ('<div class="vpos-li-ok">' + this.loggedOutMsg + '</div>') : ''}
        <input class="vpos-li vpos-li-user" placeholder="User ID / Email" autocomplete="username">
        <input class="vpos-li vpos-li-pass" type="password" placeholder="Password" autocomplete="current-password">
        <button class="vpos-li-btn" id="vpos-li-go">Sign In</button>
        <div class="vpos-li-or">— or scan your QR badge —</div>
        <button class="vpos-li-qr" id="vpos-li-scan">&#128247; Scan QR Code (camera)</button>
        <label class="vpos-li-up"><input type="file" accept="image/*" id="vpos-li-file" style="display:none">&#128247; Upload QR image to log in</label>
        <div class="vpos-li-or">— or paste badge code —</div>
        <input class="vpos-li vpos-li-code" id="vpos-li-code" placeholder="user|password">
        <button class="vpos-li-qr" id="vpos-li-codego">Use code</button>
        <div class="vpos-li-err" id="vpos-li-err"></div>
        <video id="vpos-video" playsinline style="display:none;width:100%;border-radius:12px;margin-top:10px"></video>
      </div>
    </div>`;

    const self = this;
    r.querySelector("#vpos-li-go").onclick = () => self.doLogin(r.querySelector(".vpos-li-user").value, r.querySelector(".vpos-li-pass").value);
    r.querySelector("#vpos-li-scan").onclick = () => self.openScanner();
    r.querySelector("#vpos-li-file").onchange = e => self.decodeImage(e.target.files[0]);
    r.querySelector("#vpos-li-codego").onclick = () => { const c = r.querySelector("#vpos-li-code").value.trim(); self.applyQr(c); };
  },

  applyQr(data) {
    if (!data) return;
    const parts = String(data).split("|");
    const u = document.querySelector(".vpos-li-user");
    const p = document.querySelector(".vpos-li-pass");
    if (u) u.value = parts[0] || "";
    if (p) p.value = parts[1] || "";
    this.doLogin(parts[0] || "", parts[1] || "");
  },

  decodeImage(file) {
    const err = document.getElementById("vpos-li-err");
    if (!file) return;
    err.textContent = "Reading QR from image...";
    const img = new Image();
    const reader = new FileReader();
    reader.onload = () => {
      img.onload = () => {
        const canvas = document.createElement("canvas");
        canvas.width = img.width; canvas.height = img.height;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        const d = ctx.getImageData(0, 0, canvas.width, canvas.height);
        let res = null;
        try { res = window.jsQR(d.data, d.width, d.height, { inversionAttempts: "attemptBoth" }); } catch (e) {}
        if (res && res.data) { err.textContent = "QR decoded."; this.applyQr(res.data); }
        else { err.textContent = "No QR found in that image."; }
      };
      img.onerror = () => err.textContent = "Could not read image.";
      img.src = reader.result;
    };
    reader.readAsDataURL(file);
  },

  async doLogin(usr, pwd) {
    const err = document.getElementById("vpos-li-err");
    if (!usr || !pwd) { err.textContent = "Enter user ID and password."; return; }
    err.textContent = "Signing in...";
    try {
      const j = await frappeLogin(usr, pwd);
      if (j && (j.message === "Logged In" || j.full_name || j.home_route || (j && !j.exc))) {
        this.user = usr; window._vposPwd = pwd;
        await this.afterLogin();
      } else {
        err.textContent = (j && j.message) ? j.message : "Login failed.";
      }
    } catch (e) { err.textContent = "Login error: " + e.message; }
  },

  async afterLogin() {
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
  },

  buildOpeningEntry(meta) {
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

  async showCloseShiftModal() {
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
          alert("✅ Shift Closed Successfully!\n\n" +
            "Closing Entry: " + result.name + "\n" +
            "Cashier: " + (result.cashier || cashierDisplayName) + "\n" +
            "Invoices by Cashier Today: " + result.total_invoices + "\n" +
            "Today's Sales: " + peso(result.grand_total) + "\n" +
            "Opening Float: " + peso(result.opening_amount) + "\n" +
            "Cash Counted: " + peso(result.closing_amount) + "\n" +
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

  openScanner() {
    const v = document.getElementById("vpos-video");
    const err = document.getElementById("vpos-li-err");
    err.textContent = "Point camera at the cashier QR badge...";
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then(stream => {
      v.srcObject = stream; v.style.display = "block"; v.play();
      const canvas = document.createElement("canvas");
      const tick = () => {
        if (v.videoWidth === 0) { requestAnimationFrame(tick); return; }
        canvas.width = v.videoWidth; canvas.height = v.videoHeight;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(v, 0, 0, canvas.width, canvas.height);
        const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
        let res = null;
        try { res = window.jsQR(img.data, img.width, img.height, { inversionAttempts: "attemptBoth" }); } catch (e) {}
        if (res && res.data) {
          stream.getTracks().forEach(t => t.stop());
          v.style.display = "none";
          this.applyQr(res.data);
        } else { requestAnimationFrame(tick); }
      };
      tick();
    }).catch(e => { err.textContent = "Camera unavailable: " + e.message; });
  },

  build() {
    const r = document.getElementById("vpos-root");
    r.innerHTML = `
    <div class="vpos-app">
      <aside class="vpos-rail">
        <div class="vpos-logo" title="ULTRA MRF POS">V</div>
        <div class="vpos-rail-nav">
          <div class="vpos-rail-ic active" data-view="pos" title="Point of Sale (Catalog & Ticket)">&#128722;</div>
          <div class="vpos-rail-ic" data-view="history" title="Transaction History">&#128202;</div>
          <div class="vpos-rail-ic" data-view="profile" title="Cashier ID Profile">&#128100;</div>
        </div>
        <div class="vpos-rail-ic close-shift" data-action="close-shift" title="Close Shift / End of Day">&#128274;</div>
        <div class="vpos-rail-ic logout" data-action="logout" title="Log out / Close">&#9211;</div>
        <div class="vpos-rail-foot" id="vpos-co">${this.company || ""}<br>${this.cashier || ""}</div>
      </aside>

      <section class="vpos-main" id="vpos-main">
        <div class="vpos-view" id="vpos-view-pos">
          <div class="vpos-bar">
            <div class="vpos-scan">
              <span class="ic">&#128269;</span>
              <input class="vpos-search" placeholder="Scan barcode or search item name/code..." autocomplete="off">
            </div>
            <div class="vpos-branch-row">
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
            </div>
          </div>
          <div class="vpos-cats" id="vpos-cats"></div>
          <div class="vpos-grid" id="vpos-products"></div>
        </div>

        <div class="vpos-view" id="vpos-view-history" style="display:none"></div>
        <div class="vpos-view" id="vpos-view-profile" style="display:none"></div>
      </section>

      <aside class="vpos-ticket" id="vpos-ticket-panel">
        <div class="vpos-tk-head">
          <div>
            <div class="vpos-tk-title">Current Ticket</div>
            <div class="vpos-tk-sub" id="vpos-clock"></div>
          </div>
          <button class="vpos-mobile-back" id="vpos-btn-mobile-back">&larr; Back to Catalog</button>
        </div>

        <div class="vpos-field">
          <label>Customer Vehicle</label>
          <input class="vpos-vin" list="vpos-veh" placeholder="Search plate or vehicle..." autocomplete="off">
          <datalist id="vpos-veh"></datalist>
        </div>

        <div class="vpos-field">
          <label>Linked Customer</label>
          <div class="vpos-cust"></div>
        </div>

        <div class="vpos-cart" id="vpos-cart"></div>

        <div class="vpos-totals">
          <div class="vpos-tot-row"><span>Items Count</span><span class="vpos-tqty">0</span></div>
          <div class="vpos-tot-row"><span>Discount Amount</span><span class="vpos-tdisc">₱0.00</span></div>
          <div class="vpos-tot-row vpos-tot-grand"><span>Total</span><span class="vpos-total">₱0.00</span></div>
        </div>

        <div class="vpos-field">
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
        </div>

        <div class="vpos-act">
          <button class="vpos-clear">Clear</button>
          <button class="vpos-print" id="vpos-print-btn">🖨 Print Receipt</button>
          <button class="vpos-charge">&#9889; Charge & Pay</button>
        </div>
      </aside>

      <!-- Floating Mobile Cart Bar -->
      <div class="vpos-mobile-cart-bar" id="vpos-mobile-cart-bar">
        <div class="vpos-mobile-cart-summary">
          <span class="vpos-mobile-cart-count"><span class="vpos-tqty">0</span> items in cart</span>
          <span class="vpos-mobile-cart-total vpos-total">₱0.00</span>
        </div>
        <button class="vpos-mobile-cart-btn" id="vpos-btn-open-mobile-cart">
          <span>Checkout & Pay</span> &rarr;
        </button>
      </div>
    </div>

    <!-- Numeric Keypad Modal -->
    <div class="vpos-keypad" id="vpos-keypad">
      <div class="vpos-kp-box">
        <div class="vpos-kp-val" id="vpos-kp-val">0</div>
        <div class="vpos-kp-keys">
          ${[7,8,9,4,5,6,1,2,3,".","0","⌫"].map(k=>'<button data-k="'+k+'">'+k+'</button>').join("")}
        </div>
        <div class="vpos-kp-actions">
          <button class="vpos-kp-clr">Clear</button>
          <button class="vpos-kp-ok">Done</button>
        </div>
      </div>
    </div>`;

    const self = this;
    r.querySelectorAll(".vpos-rail-ic").forEach(b => b.onclick = () => {
      const act = b.getAttribute("data-action");
      if (act === "logout") { self.logout(); return; }
      if (act === "close-shift") { self.showCloseShiftModal(); return; }
      self.switchView(b.getAttribute("data-view"));
    });

    r.querySelector(".vpos-search").addEventListener("keydown", e => { if (e.key === "Enter") self.search(); });
    r.querySelector(".vpos-search").addEventListener("input", () => {
      clearTimeout(self._searchT);
      self._searchT = setTimeout(() => self.search(), 280);
    });

    // Auto-selected branch (no dropdown)
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
    });

    const topCloseBtn = r.querySelector("#vpos-btn-top-close-shift");
    if (topCloseBtn) topCloseBtn.onclick = () => self.showCloseShiftModal();

    const st = r.querySelector("#vpos-stock-toggle");
    st.onclick = () => {
      self.onlyStock = !self.onlyStock;
      st.classList.toggle("on", self.onlyStock);
      st.textContent = "In Stock: " + (self.onlyStock ? "ON" : "OFF");
      self.search();
    };

    r.querySelector(".vpos-paid").addEventListener("click", () => self.openKeypad());
    r.querySelectorAll(".vpos-quick button").forEach(b => b.onclick = () => self.quickAdd(flt(b.getAttribute("data-q"))));
    r.querySelector(".vpos-clear").onclick = () => self.clear();
    r.querySelector(".vpos-charge").onclick = () => self.charge();
    const printBtn = r.querySelector("#vpos-print-btn");
    if (printBtn) {
      printBtn.onclick = () => self.printReceipt();
      printBtn.disabled = !(self.cart.length || self._recentSale);
    }

    const vin = r.querySelector(".vpos-vin");
    vin.addEventListener("input", () => {
      clearTimeout(self._vt);
      self._vt = setTimeout(() => self.searchVeh(vin.value), 220);
    });
    vin.addEventListener("change", () => self.onVeh(vin.value));

    // Mobile Ticket Buttons
    const mobCartBtn = r.querySelector("#vpos-btn-open-mobile-cart");
    if (mobCartBtn) mobCartBtn.onclick = () => self.toggleMobileTicket(true);

    const mobBackBtn = r.querySelector("#vpos-btn-mobile-back");
    if (mobBackBtn) mobBackBtn.onclick = () => self.toggleMobileTicket(false);

    this.clock();
    setInterval(() => this.clock(), 1000);
    this.initTip();
    this.cartRender();
    this.totals();
  },

  toggleMobileTicket(show) {
    const p = document.getElementById("vpos-ticket-panel");
    const bar = document.getElementById("vpos-mobile-cart-bar");
    if (p) {
      if (show) p.classList.add("mobile-active");
      else p.classList.remove("mobile-active");
    }
    if (bar) bar.style.display = show ? "none" : (this.cart.length ? "flex" : "none");
  },

  async load() {
    const meta = await api("vehicle_management.vehicle_management.pos_api.get_meta");
    const box = document.getElementById("vpos-cats");
    if (meta && box) {
      box.innerHTML = "";
      this.cat(box, "", "All Categories", true);
      (meta.categories || []).forEach(g => this.cat(box, g, g, false));
    }
    // Ensure company is set from cashier employee record or default to ULTRA MRF
    if (!this.company) {
      this.company = "ULTRA MRF";
    }
    const bName = document.getElementById("vpos-branch-name");
    if (bName) bName.textContent = this.company || "All Branches";
    const coFoot = document.getElementById("vpos-co");
    if (coFoot) coFoot.innerHTML = (this.company || "") + "<br>" + (this.cashier || "");
    this.totals();
    this.search();
    this.history = await api("vm_pos_history") || [];
  },

  cat(box, val, label, active) {
    const b = document.createElement("button");
    b.className = "vpos-cat" + (active ? " active" : "");
    b.textContent = label;
    b.setAttribute("data-cat", val);
    b.onclick = () => {
      box.querySelectorAll(".vpos-cat").forEach(x => x.classList.remove("active"));
      b.classList.add("active");
      this.category = val || null;
      this.search();
    };
    box.appendChild(b);
  },

  switchView(v) {
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
  },

  renderPOS() {
    const view = document.getElementById("vpos-view-pos");
    if (!view) return;
    const grid = view.querySelector("#vpos-products");
    if (!grid.innerHTML) this.search();
  },

  async fetchHistory(params = {}) {
    const view = document.getElementById("vpos-view-history");
    const countEl = document.getElementById("vpos-hist-count");
    const listEl = document.getElementById("vpos-hist-list");
    const refBtn = document.getElementById("vpos-hist-refresh");

    if (refBtn) { refBtn.disabled = true; refBtn.textContent = "⏳ Syncing..."; }
    if (listEl) listEl.innerHTML = '<div class="vpos-empty" style="padding:24px;">🔄 Fetching real-time transactions...</div>';

    this.histPeriod = params.period !== undefined ? params.period : (this.histPeriod || "all");
    this.histFromDate = params.from_date !== undefined ? params.from_date : (this.histFromDate || "");
    this.histToDate = params.to_date !== undefined ? params.to_date : (this.histToDate || "");
    this.histSearch = params.search !== undefined ? params.search : (this.histSearch || "");

    const histCo = (this.company === "All Branches" || !this.company) ? "" : this.company;
    const queryParams = {
      period: this.histPeriod,
      from_date: this.histFromDate,
      to_date: this.histToDate,
      search: this.histSearch,
      company: histCo
    };

    let list = [];
    try {
      list = await api("vm_pos_history", queryParams) || [];
    } catch (e) {
      console.error("fetchHistory error:", e);
    }
    this.history = list;
    if (refBtn) { refBtn.disabled = false; refBtn.textContent = "🔄 Refresh"; }
    this.renderHistoryList();
    return list;
  },

  renderHistory() {
    const view = document.getElementById("vpos-view-history");
    if (!view) return;

    // Render history container shell if not already built
    if (!view.querySelector(".vpos-hist-bar")) {
      const todayIso = new Date().toISOString().split("T")[0];
      view.innerHTML = `
      <div class="vpos-hist-box">
        <div class="vpos-hist-bar">
          <div class="vpos-hist-title">
            <h3>Transaction History</h3>
            <span class="vpos-hist-badge" id="vpos-hist-count">0 invoices</span>
          </div>
          <div class="vpos-hist-controls">
            <div class="vpos-hist-pills" id="vpos-hist-pills">
              <button class="vpos-hist-pill active" data-period="all">All</button>
              <button class="vpos-hist-pill" data-period="today">Today</button>
              <button class="vpos-hist-pill" data-period="month">This Month</button>
            </div>
            <select class="vpos-hist-dt" id="vpos-hist-branch-filter" style="height:34px;background:#fff;border:1px solid var(--line);border-radius:8px;padding:0 8px;font-size:12px;font-weight:600;color:var(--txt);" title="Filter by Branch">
              <option value="">🏢 All Branches</option>
              <option value="ULTRA MRF" selected>ULTRA MRF</option>
              <option value="Ultra MRF Dau Main">Ultra MRF Dau Main</option>
              <option value="Ultra MRF Dau Annex">Ultra MRF Dau Annex</option>
            </select>
            <div class="vpos-hist-dates">
              <input type="date" id="vpos-hist-from" class="vpos-hist-dt" title="From Date">
              <span style="font-size:12px;color:var(--muted)">to</span>
              <input type="date" id="vpos-hist-to" class="vpos-hist-dt" title="To Date">
              <button class="vpos-hist-btn primary" id="vpos-hist-apply" style="height:34px">Apply</button>
            </div>
            <button class="vpos-hist-btn" id="vpos-hist-refresh">🔄 Refresh</button>
          </div>
        </div>

        <div class="vpos-hist-search-box">
          <span style="font-size:16px;opacity:.6">🔍</span>
          <input type="text" id="vpos-hist-search" placeholder="Search customer name, vehicle plate, or invoice #...">
        </div>

        <div class="vpos-hist-list" id="vpos-hist-list"></div>
      </div>`;

      // Bind filter pill buttons
      const self = this;
      view.querySelectorAll(".vpos-hist-pill").forEach(p => {
        p.onclick = () => {
          view.querySelectorAll(".vpos-hist-pill").forEach(x => x.classList.remove("active"));
          p.classList.add("active");
          const per = p.getAttribute("data-period");
          self.fetchHistory({ period: per, from_date: "", to_date: "" });
        };
      });

      // Bind date range apply
      const applyBtn = view.querySelector("#vpos-hist-apply");
      if (applyBtn) {
        applyBtn.onclick = () => {
          view.querySelectorAll(".vpos-hist-pill").forEach(x => x.classList.remove("active"));
          const f = (view.querySelector("#vpos-hist-from") || {}).value || "";
          const t = (view.querySelector("#vpos-hist-to") || {}).value || "";
          self.fetchHistory({ period: "custom", from_date: f, to_date: t });
        };
      }

      // Bind refresh button
      const refBtn = view.querySelector("#vpos-hist-refresh");
      if (refBtn) refBtn.onclick = () => self.fetchHistory();

      // Bind branch filter change
      const brSelect = view.querySelector("#vpos-hist-branch-filter");
      if (brSelect) {
        brSelect.value = self.company || "ULTRA MRF";
        brSelect.onchange = () => {
          self.fetchHistory({ company: brSelect.value });
        };
      }

      // Bind search input with debounce
      const sInput = view.querySelector("#vpos-hist-search");
      if (sInput) {
        sInput.oninput = () => {
          clearTimeout(self._histST);
          self._histST = setTimeout(() => {
            self.fetchHistory({ search: sInput.value });
          }, 300);
        };
      }
    }

    // Always trigger a real-time fetch when opening the tab
    this.fetchHistory({ period: this.histPeriod || "all" });
  },

  renderHistoryList() {
    const listEl = document.getElementById("vpos-hist-list");
    const countEl = document.getElementById("vpos-hist-count");
    if (!listEl) return;

    const list = this.history || [];
    if (countEl) countEl.textContent = list.length + (list.length === 1 ? " invoice" : " invoices");

    if (!list.length) {
      listEl.innerHTML = '<div class="vpos-empty" style="padding:40px;background:#fff;border-radius:16px;border:1px solid var(--line);">No transactions found matching the selected filter/date range.</div>';
      return;
    }

    listEl.innerHTML = list.map(t => {
      const isPaid = (t.status === "Paid" || flt(t.paid_amount) >= flt(t.total_amount));
      const posLink = t.pos_invoice ? `<span class="vpos-hist-tag desk-link" onclick="window.open('/desk#Form/POS Invoice/${encodeURIComponent(t.pos_invoice)}', '_blank')">🔗 ${t.pos_invoice}</span>` : "";
      const vehDisplay = (t.plate_no || t.vehicle) ? `🚗 <b>${t.plate_no || t.vehicle}</b>` : "";
      const remDisplay = t.remarks ? `<div style="font-size:11px;color:var(--muted);margin-top:2px;">📝 ${t.remarks}</div>` : "";

      return `
      <div class="vpos-hist-card">
        <div class="vpos-hist-top">
          <div class="vpos-hist-code" onclick="window.open('/desk#Form/POS Invoice/${encodeURIComponent(t.name)}', '_blank')" title="Open POS Invoice in Desk">${t.name}</div>
          <div class="vpos-hist-time">${t.timestamp || t.posting_date || ""}</div>
        </div>
        <div class="vpos-hist-mid">
          <div class="vpos-hist-cust">${t.customer_name || "Walk-in Customer"}</div>
          <div class="vpos-hist-sub">${vehDisplay} ${t.company ? "· 🏢 " + t.company : ""}</div>
        </div>
        ${remDisplay}
        <div class="vpos-hist-foot">
          <div class="vpos-hist-amt">${peso(t.total_amount)}</div>
          <div class="vpos-hist-tags">
            <button class="vpos-hist-print-btn" type="button" onclick="event.stopPropagation(); POS.showReceiptForInvoice('${t.name}')">🖨 Print Receipt</button>
            <span class="vpos-hist-tag">${t.payment_method || "Cash"}</span>
            <span class="vpos-hist-tag ${isPaid ? 'paid' : ''}">${isPaid ? '✓ Paid' : 'Draft'}</span>
          </div>
        </div>
      </div>`;
    }).join("");
  },

  renderProfile() {
    const view = document.getElementById("vpos-view-profile");
    if (!view) return;
    const qrData = (this.email || this.cashier || "") + "|" + (window._vposPwd || "");
    let svg = "";
    try {
      const qr = window.qrcode(0, "M");
      qr.addData(qrData);
      qr.make();
      svg = qr.createSvgTag({ cellSize: 6, margin: 8, scalable: true });
    } catch (e) { svg = "<div style='color:#b91c1c'>QR unavailable</div>"; }

    view.innerHTML = `
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
    </div>`;

    const dl = document.getElementById("vpos-prof-dl");
    if (dl) dl.onclick = () => POS.downloadCard();
    const cp = document.getElementById("vpos-prof-copy");
    if (cp) cp.onclick = () => {
      if (navigator.clipboard) navigator.clipboard.writeText(qrData);
      cp.textContent = "Copied!";
      setTimeout(() => cp.textContent = "\uD83D\uDCCB Copy Badge Code", 1200);
    };
  },

  downloadCard() {
    const dlBtn = document.getElementById("vpos-prof-dl");
    const origText = dlBtn ? dlBtn.textContent : "";
    const setStatus = (msg, color) => {
      if (dlBtn) { dlBtn.textContent = msg; dlBtn.style.color = color || ""; }
    };
    setStatus("\u23f3 Generating badge...", "#0fa76d");

    // CR80 standard card: 85.6mm × 54mm
    // At 300 DPI = 85.6 × 11.811 = 1011 px,  54 × 11.811 = 638 px
    // Use exact integer values so canvas renders pixel-perfectly
    const CW = 1012;  // card pixel width  (85.6mm @ 300dpi)
    const CH = 638;   // card pixel height (54mm  @ 300dpi)

    // Scale factor: all SVG drawing coords are in CW×CH space
    // (no separate viewBox — width=CW height=CH, coordinates 1:1)
    const qrData = (this.email || this.cashier || "") + "|" + (window._vposPwd || "");
    let qrInner = "", vb = "0 0 100 100";
    try {
      const q = window.qrcode(0, "M"); q.addData(qrData); q.make();
      const tag = q.createSvgTag({ cellSize: 6, margin: 4, scalable: true });
      vb = (tag.match(/viewBox="([^"]+)"/) || [])[1] || vb;
      qrInner = tag.replace(/^<svg[^>]*>/, "").replace(/<\/svg>$/, "");
    } catch (e) { console.warn("QR gen", e); }

    const esc = s => String(s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

    // Layout constants (in 1012×638 pixel space)
    const HEADER_H = 100;      // dark header bar height
    const LEFT_W   = 570;      // left info column width
    const QR_X     = LEFT_W + 10;
    const QR_Y     = HEADER_H + 10;
    const QR_SIZE  = CW - QR_X - 14; // remaining right column

    const infoLines = [
      ["Employee",    this.empName || this.employee || "\u2014"],
      ["Emp #",       this.empNo   || "\u2014"],
      ["Designation", this.designation || "\u2014"],
      ["Branch",      this.branch  || "\u2014"],
      ["Department",  this.department || "\u2014"],
      ["Email",       this.email   || this.cashier || ""]
    ];

    let rows = "";
    infoLines.forEach((p, i) => {
      const y = HEADER_H + 54 + i * 52;
      rows += `<text x="36" y="${y}" font-family="Arial,Helvetica,sans-serif" font-size="22" fill="#7c8f8a" font-weight="600">${esc(p[0])}</text>`;
      rows += `<text x="36" y="${y + 28}" font-family="Arial,Helvetica,sans-serif" font-size="28" fill="#0c1a18" font-weight="700" clip-path="url(#lclip)">${esc(p[1])}</text>`;
    });

    const svgMarkup = `<svg xmlns="http://www.w3.org/2000/svg" width="${CW}" height="${CH}">
  <defs>
    <linearGradient id="hdr" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0c1a18"/>
      <stop offset="1" stop-color="#174033"/>
    </linearGradient>
    <linearGradient id="mintg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#16c784"/>
      <stop offset="1" stop-color="#0fa76d"/>
    </linearGradient>
    <clipPath id="lclip">
      <rect x="36" y="0" width="${LEFT_W - 50}" height="${CH}"/>
    </clipPath>
  </defs>

  <!-- Card white background with rounded corners -->
  <rect width="${CW}" height="${CH}" rx="18" fill="#ffffff"/>

  <!-- Dark header bar -->
  <rect width="${CW}" height="${HEADER_H}" rx="18" fill="url(#hdr)"/>
  <rect y="${HEADER_H - 18}" width="${CW}" height="18" fill="url(#hdr)"/>

  <!-- Mint accent logo badge -->
  <rect x="28" y="22" width="58" height="58" rx="14" fill="url(#mintg)"/>
  <text x="57" y="63" font-family="Arial,Helvetica,sans-serif" font-size="38" font-weight="900" fill="#04201a" text-anchor="middle">V</text>

  <!-- Company name -->
  <text x="100" y="52" font-family="Arial,Helvetica,sans-serif" font-size="26" font-weight="700" fill="#ffffff">${esc(this.company || "")}</text>
  <text x="100" y="80" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="400" fill="#9fc3b8">Vehicle Management System</text>

  <!-- CASHIER ID pill label -->
  <rect x="${CW - 170}" y="28" width="142" height="46" rx="23" fill="#16c784" opacity="0.15"/>
  <text x="${CW - 99}" y="58" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="800" letter-spacing="3" fill="#16c784" text-anchor="middle">CASHIER ID</text>

  <!-- Vertical divider -->
  <line x1="${LEFT_W}" y1="${HEADER_H + 16}" x2="${LEFT_W}" y2="${CH - 16}" stroke="#dde9e4" stroke-width="2"/>

  <!-- Cashier name (large) -->
  <text x="36" y="${HEADER_H + 44}" font-family="Arial,Helvetica,sans-serif" font-size="34" font-weight="900" fill="#0c1a18" clip-path="url(#lclip)">${esc(this.empName || this.employee || "\u2014")}</text>

  <!-- Info rows (label + value pairs) -->
  ${rows}

  <!-- QR Code area -->
  <rect x="${QR_X}" y="${QR_Y}" width="${QR_SIZE}" height="${QR_SIZE}" rx="10" fill="#f8fcfa"/>
  <svg x="${QR_X + 6}" y="${QR_Y + 6}" width="${QR_SIZE - 12}" height="${QR_SIZE - 12}" viewBox="${vb}">${qrInner}</svg>
  <text x="${QR_X + QR_SIZE / 2}" y="${QR_Y + QR_SIZE + 28}" font-family="Arial,Helvetica,sans-serif" font-size="19" fill="#7c8f8a" text-anchor="middle">Scan to log in</text>

  <!-- Footer separator + tagline -->
  <line x1="28" y1="${CH - 34}" x2="${CW - 28}" y2="${CH - 34}" stroke="#eef7f3" stroke-width="1.5"/>
  <text x="${CW / 2}" y="${CH - 12}" font-family="Arial,Helvetica,sans-serif" font-size="16" fill="#9fc3b8" text-anchor="middle">Ultra MRF Automotive Group  •  ${new Date().toLocaleDateString("en-PH", {year:"numeric",month:"long"})}</text>

  <!-- Top-right corner badge border -->
  <rect x="0.5" y="0.5" width="${CW - 1}" height="${CH - 1}" rx="17.5" fill="none" stroke="#dde9e4" stroke-width="1"/>
</svg>`;

    const fname = (this.empNo || this.cashier || "cashier").replace(/[^a-zA-Z0-9_-]/g, "_") + "-cashier-id";

    // Method 1: Render SVG → Canvas → download exact-size PNG
    const tryPNG = () => {
      try {
        const canvas = document.createElement("canvas");
        canvas.width  = CW;
        canvas.height = CH;
        const ctx = canvas.getContext("2d");
        if (!ctx) throw new Error("no ctx");
        const blob0 = new Blob([svgMarkup], { type: "image/svg+xml;charset=utf-8" });
        const url0  = URL.createObjectURL(blob0);
        const img   = new Image();
        img.onload = () => {
          // Draw only the card — canvas is exactly CW×CH
          ctx.drawImage(img, 0, 0, CW, CH);
          URL.revokeObjectURL(url0);
          canvas.toBlob(blob => {
            if (!blob) { trySVG(); return; }
            const pu = URL.createObjectURL(blob);
            const a  = document.createElement("a");
            a.href = pu; a.download = fname + ".png";
            document.body.appendChild(a); a.click(); document.body.removeChild(a);
            setTimeout(() => URL.revokeObjectURL(pu), 6000);
            setStatus("\u2713 Downloaded PNG (" + CW + "\xd7" + CH + " px)!", "#0fa76d");
            setTimeout(() => { if (dlBtn) { dlBtn.textContent = origText; dlBtn.style.color = ""; } }, 2800);
          }, "image/png");
        };
        img.onerror = () => { URL.revokeObjectURL(url0); trySVG(); };
        img.width  = CW;
        img.height = CH;
        img.src = url0;
      } catch (e) { trySVG(); }
    };

    // Method 2: SVG file download
    const trySVG = () => {
      try {
        const blob = new Blob([svgMarkup], { type: "image/svg+xml" });
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement("a");
        a.href = url; a.download = fname + ".svg";
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(url), 6000);
        setStatus("\u2713 Downloaded SVG!", "#0fa76d");
        setTimeout(() => { if (dlBtn) { dlBtn.textContent = origText; dlBtn.style.color = ""; } }, 2500);
      } catch (e2) {
        // Last resort: open in new tab
        const w = window.open("", "_blank");
        if (w) {
          w.document.open();
          w.document.write("<!DOCTYPE html><html><head><title>Cashier Badge</title></head>" +
            "<body style='margin:0;background:#111;display:flex;align-items:center;justify-content:center;min-height:100vh'>" +
            "<div style='font-family:sans-serif;position:fixed;top:12px;left:50%;transform:translateX(-50%);background:#fff;padding:10px 18px;border-radius:8px;font-size:14px;box-shadow:0 4px 14px rgba(0,0,0,.4)'>" +
            "Right-click the card \u2192 <b>Save image as\u2026</b></div>" + svgMarkup + "</body></html>");
          w.document.close();
        }
        setStatus("\u2197 Opened in new tab \u2013 save manually", "#f5a623");
        setTimeout(() => { if (dlBtn) { dlBtn.textContent = origText; dlBtn.style.color = ""; } }, 3500);
      }
    };

    tryPNG();
  },




  clock() {
    const d = new Date();
    const t = d.toLocaleTimeString("en-PH", { hour: "2-digit", minute: "2-digit" });
    const dt = d.toLocaleDateString("en-PH", { month: "short", day: "numeric" });
    const el = document.getElementById("vpos-clock");
    if (el) el.textContent = dt + " · " + t;
  },

  async searchVeh(q) {
    if (!q || q.length < 1) return;
    const rows = await api("vm_pos_vehicles", { txt: q }) || [];
    const dl = document.getElementById("vpos-veh");
    if (dl) {
      dl.innerHTML = "";
      rows.forEach(v => {
        const o = document.createElement("option");
        o.value = v.name;
        o.textContent = (v.plate_no ? v.plate_no + " — " : "") + (v.customer_name || v.customer);
        dl.appendChild(o);
      });
    }
  },

  async onVeh(vehicle) {
    this.vehicle = vehicle || null;
    const disp = document.querySelector(".vpos-cust");
    if (!vehicle) { this.customer = null; if (disp) disp.textContent = ""; return; }
    const d = await api("vm_pos_vehicle_customer", { vehicle: vehicle });
    if (d && d.customer) {
      this.customer = d.customer;
      if (disp) disp.textContent = d.customer_name ? (d.customer + " — " + d.customer_name) : d.customer;
    } else {
      this.customer = null;
      if (disp) disp.textContent = "";
      alert("Selected Vehicle has no linked Customer.");
    }
  },

  async search() {
    const txt = (document.querySelector(".vpos-search") || {}).value || "";
    const items = await api("vm_pos_get_items", {
      txt: txt,
      category: this.category || "",
      company: this.company || "",
      only_stock: this.onlyStock ? 1 : 0
    }) || [];
    items.forEach(it => {
      if (it.stock != null) {
        this.STOCK[it.code] = { stock: flt(it.stock), bins: [] };
      }
    });
    this.render(items);
  },

  async render(items) {
    const box = document.getElementById("vpos-products");
    if (!box) return;
    box.innerHTML = "";
    if (!items.length) {
      box.innerHTML = this.onlyStock
        ? '<div class="vpos-empty">No items currently in stock for the selected company/filter.</div>'
        : '<div class="vpos-empty">No matching products or services.</div>';
      return;
    }
    this._items = items;
    let visible = items;
    if (this.onlyStock) {
      visible = items.filter(it => flt(it.stock != null ? it.stock : ((this.STOCK[it.code] || {}).stock)) > 0);
    }
    if (!visible.length) {
      box.innerHTML = '<div class="vpos-empty">No items currently in stock for the selected company/filter.</div>';
      return;
    }
    const shown = this.showAll ? visible : visible.slice(0, this.PROD_LIMIT);
    const self = this;
    shown.forEach(it => self.card(it, box));
    if (visible.length > this.PROD_LIMIT) {
      const more = document.createElement("button");
      more.className = "vpos-card vpos-more";
      more.style.cssText = "display:flex;align-items:center;justify-content:center;cursor:pointer;border-style:dashed;color:var(--mint-d);font-weight:700;font-size:13px;min-height:120px;";
      const left = visible.length - shown.length;
      more.textContent = this.showAll ? ("Show less (" + this.PROD_LIMIT + " shown)") : ("Show all items (" + left + " more)");
      more.onclick = () => { self.showAll = !self.showAll; self.render(items); };
      box.appendChild(more);
    }
    this.loadStock(shown);
  },

  async loadStock(list) {
    if (!list || !list.length) return;
    const codes = list.map(it => it.code).join(",");
    const data = await api("vm_pos_stock", { codes: codes, company: this.company || "" }) || {};
    this.STOCK = Object.assign(this.STOCK || {}, data);
    list.forEach(it => {
      const el = document.querySelector('[data-code="' + CSS.escape(it.code) + '"]');
      if (!el) return;
      const st = data[it.code];
      const stockEl = el.querySelector(".vpos-card-stock");
      if (stockEl) {
        const s = flt(st ? st.stock : (it.stock != null ? it.stock : 0));
        stockEl.textContent = "Stock: " + s;
        if (s <= 0) {
          stockEl.classList.add("zero");
          stockEl.style.color = "#e55353";
        } else {
          stockEl.classList.remove("zero");
          stockEl.style.color = "#16c784";
        }
      }
      if (st) el.setAttribute("data-tip", this.stockTip(st));
    });
  },

  stockTip(st) {
    let s = "On hand: " + flt(st.stock) + "\n";
    (st.bins || []).forEach(b => { s += "\n" + b.warehouse + "  " + flt(b.qty) + (b.bin ? ("  · bin " + b.bin) : ""); });
    return s.trim();
  },

  getCategoryIcon(group, name) {
    const s = ((group || "") + " " + (name || "")).toLowerCase();
    if (s.includes("tire") || s.includes("tyre") || s.includes("wheel") || s.includes("rim") || s.includes("mag")) return "🛞";
    if (s.includes("oil") || s.includes("lube") || s.includes("lubricant") || s.includes("fluid")) return "🛢️";
    if (s.includes("service") || s.includes("labor") || s.includes("alignment") || s.includes("pms") || s.includes("repair")) return "🔧";
    if (s.includes("battery")) return "🔋";
    if (s.includes("brake") || s.includes("pad") || s.includes("rotor")) return "🛑";
    if (s.includes("filter")) return "🌪️";
    return "📦";
  },

  card(it, box) {
    const self = this;
    const name = it.name || it.code;
    const rate = flt(it.rate) || 0;
    const card = document.createElement("div");
    card.className = "vpos-card";
    card.setAttribute("data-code", it.code);
    const stock = this.STOCK && this.STOCK[it.code] ? this.STOCK[it.code].stock : null;
    const tip = this.STOCK && this.STOCK[it.code] ? this.stockTip(this.STOCK[it.code]) : "";

    let thumbHtml = "";
    if (it.image) {
      thumbHtml = `<div class="vpos-thumb"><img src="${it.image}" alt="${name}" loading="lazy" onerror="this.onerror=null;this.parentElement.innerHTML='<div class=\'vpos-thumb-placeholder\'><span class=\'ico\'>${self.getCategoryIcon(it.group, name)}</span><span>${it.group || 'Product'}</span></div>';"></div>`;
    } else {
      thumbHtml = `<div class="vpos-thumb"><div class="vpos-thumb-placeholder"><span class="ico">${self.getCategoryIcon(it.group, name)}</span><span>${it.group || 'Item'}</span></div></div>`;
    }

    card.innerHTML = `
      ${thumbHtml}
      <div class="vpos-card-name" title="${name}">${name}</div>
      <div class="vpos-card-code">${it.code}</div>
      <div class="vpos-card-stock">${stock == null ? "Stock: …" : "Stock: " + flt(stock)}</div>
      <div class="vpos-card-foot">
        <div class="vpos-card-rate" title="${peso(rate)}">${peso(rate)}</div>
        <button class="vpos-card-add" type="button">+ ADD</button>
      </div>`;

    if (tip) card.setAttribute("data-tip", tip);
    const inc = this.cart.find(c => c.item_code === it.code);
    if (inc) {
      const b = document.createElement("div");
      b.className = "vpos-card-badge";
      b.textContent = inc.qty + " in cart";
      card.appendChild(b);
    }
    card.onclick = () => self.add(it.code, name, rate, it.uom);
    card.querySelector(".vpos-card-add").onclick = (e) => {
      e.stopPropagation();
      self.add(it.code, name, rate, it.uom);
    };
    box.appendChild(card);
  },

  add(code, name, rate, uom) {
    const ex = this.cart.find(c => c.item_code === code);
    if (ex) ex.qty += 1;
    else this.cart.push({ item_code: code, item_name: name, qty: 1, rate: rate, uom: uom, discount_amount: 0 });
    this.cartRender();
    this.totals();
    this.search();
  },

  cartRender() {
    const box = document.getElementById("vpos-cart");
    if (!box) return;
    box.innerHTML = "";
    if (!this.cart.length) {
      box.innerHTML = '<div class="vpos-empty">Cart is empty.<br>Tap items in catalog to add.</div>';
      return;
    }
    const self = this;
    this.cart.forEach((c, i) => {
      const amt = flt(c.qty) * flt(c.rate) - flt(c.discount_amount);
      const row = document.createElement("div");
      row.className = "vpos-row";
      row.innerHTML = `
        <div class="vpos-row-info">
          <div class="vpos-row-name">${c.item_name}</div>
          <div class="vpos-row-meta">${peso(c.rate)} · ${c.uom || "Unit"}</div>
        </div>
        <div class="vpos-qty">
          <button class="vpos-dec">−</button>
          <input class="vpos-qty-in" type="number" min="1" value="${c.qty}">
          <button class="vpos-inc">+</button>
        </div>
        <input class="vpos-row-disc" type="number" min="0" step="0.01" value="${flt(c.discount_amount)}" title="Discount">
        <div class="vpos-row-amt">${peso(amt)}</div>
        <button class="vpos-remove" title="Remove item">×</button>`;

      row.querySelector(".vpos-inc").onclick = () => { c.qty += 1; self.cartRender(); self.totals(); };
      row.querySelector(".vpos-dec").onclick = () => { c.qty = Math.max(1, c.qty - 1); self.cartRender(); self.totals(); };
      row.querySelector(".vpos-qty-in").onchange = e => { c.qty = Math.max(1, parseInt(e.target.value) || 1); self.cartRender(); self.totals(); };
      row.querySelector(".vpos-row-disc").onchange = e => { c.discount_amount = Math.max(0, flt(e.target.value)); self.cartRender(); self.totals(); };
      row.querySelector(".vpos-remove").onclick = () => { self.cart.splice(i, 1); self.cartRender(); self.totals(); self.search(); };
      box.appendChild(row);
    });
  },

  totals() {
    let tq = 0, td = 0, tot = 0;
    this.cart.forEach(c => {
      tq += flt(c.qty);
      td += flt(c.discount_amount);
      tot += flt(c.qty) * flt(c.rate) - flt(c.discount_amount);
    });
    this.total = tot;

    document.querySelectorAll(".vpos-tqty").forEach(el => el.textContent = tq);
    document.querySelectorAll(".vpos-tdisc").forEach(el => el.textContent = peso(td));
    document.querySelectorAll(".vpos-total").forEach(el => el.textContent = peso(tot));

    const paidInp = document.querySelector(".vpos-paid");
    const paid = flt(paidInp ? paidInp.value : 0);
    const balEl = document.querySelector(".vpos-balance");
    if (balEl) balEl.textContent = peso(flt(paid - tot));

    const chargeBtn = document.querySelector(".vpos-charge");
    if (chargeBtn) {
      chargeBtn.disabled = !(this.cart.length && this.vehicle && this.customer && this.company && paid >= tot);
    }
    const printBtn = document.querySelector("#vpos-print-btn");
    if (printBtn) {
      printBtn.disabled = !(this.cart.length || this._recentSale);
    }

    // Update Floating Mobile Cart Bar
    const mobBar = document.getElementById("vpos-mobile-cart-bar");
    if (mobBar) {
      mobBar.style.display = (this.cart.length && !document.getElementById("vpos-ticket-panel").classList.contains("mobile-active")) ? "flex" : "none";
    }
  },

  openKeypad() {
    const kp = document.getElementById("vpos-keypad");
    this._kp = flt(document.querySelector(".vpos-paid").value) || 0;
    document.getElementById("vpos-kp-val").textContent = this._kp;
    kp.classList.add("open");
    const self = this;
    kp.querySelectorAll("[data-k]").forEach(b => b.onclick = () => {
      const k = b.getAttribute("data-k");
      if (k === "⌫") { self._kp = Math.floor(self._kp / 10); }
      else if (k === ".") { if (!String(self._kp).includes(".")) self._kp = self._kp + "."; }
      else { self._kp = (self._kp === 0 ? "" + k : self._kp + "" + k); }
      document.getElementById("vpos-kp-val").textContent = self._kp;
    });
    kp.querySelector(".vpos-kp-clr").onclick = () => { self._kp = 0; document.getElementById("vpos-kp-val").textContent = "0"; };
    kp.querySelector(".vpos-kp-ok").onclick = () => {
      document.querySelector(".vpos-paid").value = self._kp;
      kp.classList.remove("open");
      self.totals();
    };
  },

  quickAdd(q) {
    const cur = flt(document.querySelector(".vpos-paid").value) || 0;
    const v = cur + q;
    document.querySelector(".vpos-paid").value = v;
    this.totals();
  },

  clear() {
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
  },

  charge() {
    const tot = this.total || 0;
    const paid = flt(document.querySelector(".vpos-paid").value) || 0;
    if (!this.cart.length) { alert("Cart is empty."); return; }
    if (!this.vehicle) { alert("Select a Customer Vehicle."); return; }
    if (!this.customer) { alert("Customer Vehicle has no linked Customer."); return; }
    if (!this.company) { alert("Company not set."); return; }
    if (paid < tot) { alert("Paid amount is less than total."); return; }
    if (!confirm("Charge " + peso(tot) + " (Change: " + peso(paid - tot) + ")?")) return;
    this.submit(tot, paid);
  },

  /* ── Transaction Submission & Receipt Suite ───────────────────────────── */
  _recentSale: null,
  _currentModalSale: null,

  async submit(tot, paid) {
    const items = this.cart.map(c => ({
      item_code: c.item_code,
      qty: c.qty,
      rate: c.rate,
      discount_amount: c.discount_amount,
      uom: c.uom
    }));
    const remEl = document.getElementById("vpos-remarks");
    const remarks = remEl ? remEl.value.trim() : "";
    const payload = {
      customer: this.customer,
      vehicle: this.vehicle || null,
      company: this.company,
      paid_amount: paid,
      payment_method: this.payment_method || "Cash",
      remarks: remarks,
      items: items
    };

    const r = await api("vm_pos_create_invoice", { data: JSON.stringify(payload) });
    if (r && r.name) {
      const now = new Date();
      const dateStr = now.toLocaleDateString("en-PH", { weekday: "long", year: "numeric", month: "long", day: "numeric" });
      const timeStr = now.toLocaleTimeString("en-PH", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
      
      this._recentSale = {
        company: this.company || "ULTRA MRF",
        cashier: this.empName || this.cashier || this.user || "Cashier",
        date: dateStr,
        time: timeStr,
        invoice_no: r.name,
        vehicle: this.vehicle || "",
        vehicle_name: this._vehicleLabel ? this._vehicleLabel() : "",
        customer: this.customer || "",
        customer_name: this._customerLabel ? this._customerLabel() : "",
        payment_method: this.payment_method || "Cash",
        paid_amount: paid,
        change_amount: paid - tot,
        total_amount: tot,
        discount_amount: flt(document.querySelector(".vpos-row-disc") ? parseFloat(document.querySelector(".vpos-row-disc").value) || 0 : 0),
        items: this.cart.map(c => ({
          item_code: c.item_code,
          item_name: c.item_name,
          qty: c.qty,
          rate: c.rate,
          amount: flt(c.qty) * flt(c.rate) - flt(c.discount_amount),
          uom: c.uom,
          discount_amount: c.discount_amount
        })),
        remarks: remarks
      };

      this.clear();
      await this.fetchHistory();
      
      // Open Receipt Modal Preview immediately
      this.showReceiptModal(this._recentSale);
    } else {
      const err = (api && api.lastError) || "Unknown server response. Please verify in console.";
      alert("⚠️ Failed to create invoice: " + err);
    }
  },

  printReceipt(sale) {
    if (sale) {
      this.showReceiptModal(sale);
    } else if (this._recentSale) {
      this.showReceiptModal(this._recentSale);
    } else if (this.cart.length) {
      this.showReceiptModal(this._buildOpenCartSale());
    } else {
      alert("No transaction or cart items to print.");
    }
  },

  async showReceiptForInvoice(invName) {
    const data = await api("vm_pos_get_invoice_receipt", { invoice_name: invName });
    if (!data || data.error) {
      alert("Could not load receipt: " + (data ? data.error : "Unknown error"));
      return;
    }
    const peso = v => "₱ " + parseFloat(v || 0).toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    let itemsHtml = "";
    (data.items || []).forEach(it => {
      const amt = flt(it.amount || (it.qty * it.rate) - flt(it.discount_amount || 0));
      itemsHtml += `
        <div class="vpos-receipt-item-block">
          <div class="vpos-receipt-item-header">
            <span>${it.item_name || it.item_code}</span>
            <span>${peso(amt)}</span>
          </div>
          <div class="vpos-receipt-item-sub">
            <span>${it.qty} ${it.uom || 'PC'} × ${peso(it.rate)}</span>
            ${it.discount_amount ? `<span style="color:#dc2626;">Disc: -${peso(it.discount_amount)}</span>` : ''}
          </div>
        </div>`;
    });
    const sale = {
      company: data.company,
      cashier: data.cashier,
      date: data.posting_date,
      time: data.posting_time,
      invoice_no: data.invoice_no,
      vehicle: data.vehicle,
      vehicle_name: data.plate_no,
      customer: data.customer,
      customer_name: data.customer_name,
      payment_method: data.payment_method,
      paid_amount: data.paid_amount,
      change_amount: data.change_amount,
      total_amount: data.total_amount,
      discount_amount: data.discount_amount,
      items_html: itemsHtml,
      items: data.items || [],
      remarks: data.remarks
    };
    this.showReceiptModal(sale);
  },

  _buildOpenCartSale() {
    const now = new Date();
    const dateStr = now.toLocaleDateString("en-PH", { weekday: "long", year: "numeric", month: "long", day: "numeric" });
    const timeStr = now.toLocaleTimeString("en-PH", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    let total = 0;
    const items = [];
    let itemsHtml = "";
    this.cart.forEach(c => {
      const amt = flt(c.qty) * flt(c.rate) - flt(c.discount_amount);
      total += amt;
      items.push({
        item_code: c.item_code,
        item_name: c.item_name,
        qty: c.qty,
        rate: c.rate,
        amount: amt,
        uom: c.uom,
        discount_amount: c.discount_amount
      });
      itemsHtml += `
        <div class="vpos-receipt-item-block">
          <div class="vpos-receipt-item-header">
            <span>${c.item_name || c.item_code}</span>
            <span>${peso(amt)}</span>
          </div>
          <div class="vpos-receipt-item-sub">
            <span>${c.qty} ${c.uom || 'PC'} × ${peso(c.rate)}</span>
            ${c.discount_amount ? `<span style="color:#dc2626;">Disc: -${peso(c.discount_amount)}</span>` : ''}
          </div>
        </div>`;
    });
    const paid = flt(document.querySelector(".vpos-paid") ? document.querySelector(".vpos-paid").value : 0) || 0;
    const change = paid - total;
    const paymentMethod = this.payment_method || "Cash";
    const cashier = this.empName || this.cashier || this.user || "Cashier";
    const company = this.company || "ULTRA MRF";
    const vehicle = this.vehicle || "";
    const customer = this.customer || "";
    const customerName = this._customerLabel ? this._customerLabel() : "";
    return {
      type: "open-cart",
      company, cashier, date: dateStr, time: timeStr,
      invoice_no: "OPEN-CART",
      vehicle, customer, customer_name: customerName,
      payment_method: paymentMethod,
      paid_amount: paid,
      change_amount: change,
      total_amount: total,
      discount_amount: flt(document.querySelector(".vpos-row-disc") ? parseFloat(document.querySelector(".vpos-row-disc").value) || 0 : 0),
      items_html: itemsHtml,
      items: items,
      remarks: ""
    };
  },

  _buildReceiptDom(sale) {
    const peso = v => "₱ " + parseFloat(v || 0).toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const company = sale.company || "ULTRA MRF";
    const cashier = sale.cashier || "Cashier";
    const date = sale.date || "";
    const time = sale.time || "";
    const invoiceNo = sale.invoice_no || "POS-0000";
    const vehicle = sale.vehicle ? (sale.vehicle + (sale.vehicle_name ? (" — " + sale.vehicle_name) : "")) : "";
    const customer = sale.customer_name ? (sale.customer + " — " + sale.customer_name) : (sale.customer || "Walk-in Customer");
    const paymentMethod = sale.payment_method || "Cash";
    const paidAmount = sale.paid_amount != null ? peso(sale.paid_amount) : "";
    const changeAmount = sale.change_amount != null ? peso(sale.change_amount) : "";
    const totalAmount = sale.total_amount != null ? peso(sale.total_amount) : "";
    const discountAmount = sale.discount_amount != null && parseFloat(sale.discount_amount) > 0 ? peso(sale.discount_amount) : "";
    const remarks = sale.remarks ? sale.remarks : "";
    
    let itemsHtml = "";
    const itemList = sale.items || sale.items_raw || [];
    if (itemList && itemList.length) {
      itemList.forEach(it => {
        const amt = flt(it.amount || (flt(it.qty) * flt(it.rate)) - flt(it.discount_amount || 0));
        itemsHtml += `
          <div class="vpos-receipt-item-block">
            <div class="vpos-receipt-item-header">
              <span>${it.item_name || it.item_code}</span>
              <span>${peso(amt)}</span>
            </div>
            <div class="vpos-receipt-item-sub">
              <span>${it.qty} ${it.uom || 'PC'} × ${peso(it.rate)}</span>
              ${it.discount_amount ? `<span style="color:#dc2626;">Disc: -${peso(it.discount_amount)}</span>` : ''}
            </div>
          </div>`;
      });
    } else if (sale.items_html) {
      itemsHtml = sale.items_html;
    } else {
      itemsHtml = '<div style="color:#64748b;font-style:italic;">No items.</div>';
    }

    const html = `
      <div class="vpos-receipt-box">
        <div class="vpos-receipt-co">${company}</div>
        <div class="vpos-receipt-sub">Vehicle Management System &amp; Services</div>
        
        <div class="vpos-receipt-not-official">
          *** THIS IS NOT AN OFFICIAL RECEIPT ***<br>
          <span style="font-size:10.5px;font-weight:600;">(ORDER SLIP / INTERNAL REFERENCE ONLY)</span>
        </div>

        <div class="vpos-receipt-row"><span>Bill / Invoice No:</span><b>${invoiceNo}</b></div>
        <div class="vpos-receipt-row"><span>Date &amp; Time:</span><span>${date} ${time ? '· ' + time : ''}</span></div>
        <div class="vpos-receipt-row"><span>Cashier / Staff:</span><span>${cashier}</span></div>

        ${(customer || vehicle) ? `
          <div class="vpos-receipt-sep"></div>
          ${customer ? `<div class="vpos-receipt-row"><span>Customer:</span><b>${customer}</b></div>` : ''}
          ${vehicle ? `<div class="vpos-receipt-row"><span>Vehicle:</span><b>${vehicle}</b></div>` : ''}
        ` : ''}

        <div class="vpos-receipt-sep-solid"></div>
        <div style="font-weight:800;font-size:12.5px;color:#0f172a;margin-bottom:4px;">ITEMS SOLD / SERVICES</div>
        <div class="vpos-receipt-items-container">${itemsHtml}</div>

        ${discountAmount ? `
          <div class="vpos-receipt-sep"></div>
          <div class="vpos-receipt-row"><span>Discount:</span><span style="color:#dc2626;">-${discountAmount}</span></div>
        ` : ''}

        <div class="vpos-receipt-sep-solid"></div>
        <div class="vpos-receipt-grand-row">
          <span>TOTAL AMOUNT:</span>
          <span>${totalAmount}</span>
        </div>
        <div class="vpos-receipt-sep"></div>

        <div class="vpos-receipt-row"><span>Payment Method:</span><b>${paymentMethod}</b></div>
        ${paidAmount ? `<div class="vpos-receipt-row"><span>Amount Tendered:</span><span>${paidAmount}</span></div>` : ''}
        ${changeAmount ? `<div class="vpos-receipt-row"><span>Change Due:</span><b style="font-size:15px;color:#10b981;">${changeAmount}</b></div>` : ''}

        ${remarks ? `
          <div class="vpos-receipt-sep"></div>
          <div class="vpos-receipt-row"><span>Remarks / Bay:</span><span>${remarks}</span></div>
        ` : ''}

        <div class="vpos-receipt-sep"></div>
        <div class="vpos-receipt-not-official" style="margin-top:8px;">
          *** THIS IS NOT AN OFFICIAL RECEIPT ***
        </div>
        <div class="vpos-receipt-foot-msg">
          Thank you for choosing ${company}!<br>
          Please keep this order slip for warranty &amp; vehicle reference.
        </div>
      </div>`;

    const div = document.createElement("div");
    div.className = "vpos-receipt-dialog-inner";
    div.innerHTML = html;
    return div;
  },

  showReceiptModal(sale) {
    if (!sale) {
      if (this._recentSale) sale = this._recentSale;
      else if (this.cart.length) sale = this._buildOpenCartSale();
      else { alert("No recent sale or cart items to display."); return; }
    }
    this._currentModalSale = sale;
    const self = this;
    const existing = document.getElementById("vpos-receipt-modal-overlay");
    if (existing) existing.remove();

    const overlay = document.createElement("div");
    overlay.className = "vpos-receipt-overlay";
    overlay.id = "vpos-receipt-modal-overlay";

    const receiptDom = this._buildReceiptDom(sale);

    overlay.innerHTML = `
      <div class="vpos-receipt-dialog">
        <div class="vpos-receipt-dialog-head">
          <span>🧾 POS Official Receipt Preview</span>
          <button class="vpos-receipt-dialog-close" id="vpos-receipt-modal-x">&times;</button>
        </div>
        <div class="vpos-receipt-dialog-body" id="vpos-receipt-modal-body">
        </div>
        <div class="vpos-receipt-dialog-foot">
          <button class="vpos-receipt-btn-print" id="vpos-receipt-modal-print">🖨 Print Receipt</button>
          <button class="vpos-receipt-btn-desk" id="vpos-receipt-modal-win" title="Open in dedicated printable window">🗗 Popup</button>
          ${sale.invoice_no && sale.invoice_no !== 'OPEN-CART' ? `<button class="vpos-receipt-btn-desk" onclick="window.open('/desk#Form/POS Invoice/${encodeURIComponent(sale.invoice_no)}', '_blank')">🔗 Desk</button>` : ''}
          <button class="vpos-receipt-btn-close" id="vpos-receipt-modal-done">Close</button>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);
    overlay.querySelector("#vpos-receipt-modal-body").appendChild(receiptDom);

    overlay.querySelector("#vpos-receipt-modal-x").onclick = () => overlay.remove();
    overlay.querySelector("#vpos-receipt-modal-done").onclick = () => overlay.remove();
    overlay.querySelector("#vpos-receipt-modal-print").onclick = () => {
      self.triggerPrint(sale);
    };
    const winBtn = overlay.querySelector("#vpos-receipt-modal-win");
    if (winBtn) {
      winBtn.onclick = () => {
        const wrap = document.querySelector("#vpos-direct-print-area") || receiptDom;
        self.openPrintWindow(wrap.innerHTML);
      };
    }
  },

  triggerPrint(sale) {
    if (!sale) {
      sale = this._currentModalSale || this._recentSale || (this.cart.length ? this._buildOpenCartSale() : null);
    }
    if (!sale) {
      alert("No transaction to print.");
      return;
    }

    const peso = v => "₱ " + parseFloat(v || 0).toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const company = sale.company || "ULTRA MRF";
    const cashier = sale.cashier || "Cashier";
    const date = sale.date || "";
    const time = sale.time || "";
    const invoiceNo = sale.invoice_no || "POS-0000";
    const vehicle = sale.vehicle ? (sale.vehicle + (sale.vehicle_name ? (" — " + sale.vehicle_name) : "")) : "";
    const customer = sale.customer_name ? (sale.customer + " — " + sale.customer_name) : (sale.customer || "Walk-in Customer");
    const paymentMethod = sale.payment_method || "Cash";
    const paidAmount = sale.paid_amount != null ? peso(sale.paid_amount) : "";
    const changeAmount = sale.change_amount != null ? peso(sale.change_amount) : "";
    const totalAmount = sale.total_amount != null ? peso(sale.total_amount) : "";
    const discountAmount = sale.discount_amount != null && parseFloat(sale.discount_amount) > 0 ? peso(sale.discount_amount) : "";
    const remarks = sale.remarks ? sale.remarks : "";

    let itemsRows = "";
    const itemList = sale.items || sale.items_raw || [];
    if (itemList && itemList.length) {
      itemList.forEach(it => {
        const amt = flt(it.amount || (flt(it.qty) * flt(it.rate)) - flt(it.discount_amount || 0));
        itemsRows += `
          <tr style="border-bottom:1px dashed #e2e8f0;">
            <td style="padding:4px 0;vertical-align:top;font-weight:700;width:62%;">${it.item_name || it.item_code}<br>
              <span style="font-size:11px;font-weight:400;color:#555;">${it.qty} ${it.uom || 'PC'} × ${peso(it.rate)}</span>
            </td>
            <td style="padding:4px 0;vertical-align:top;text-align:right;font-weight:700;width:38%;">${peso(amt)}</td>
          </tr>`;
      });
    } else if (sale.items_html) {
      itemsRows = sale.items_html;
    } else {
      itemsRows = '<tr><td colspan="2" style="color:#555;font-style:italic;">No items.</td></tr>';
    }

    const receiptMarkup = `
      <div class="vpos-receipt-print-wrapper" style="width:100%;max-width:76mm;margin:0 auto;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Courier New',monospace;font-size:12px;line-height:1.35;color:#000;background:#fff;padding:4mm 2mm;">
        <div style="font-size:16px;font-weight:900;text-align:center;text-transform:uppercase;color:#000;">${company}</div>
        <div style="font-size:11px;text-align:center;color:#444;margin-top:1px;">Vehicle Management System &amp; Services</div>

        <div style="margin:6px 0;padding:4px 6px;border:1.5px dashed #000;text-align:center;font-weight:800;font-size:10.5px;color:#000;background:#f9f9f9;">
          *** THIS IS NOT AN OFFICIAL RECEIPT ***<br>
          <span style="font-size:9px;font-weight:600;">(ORDER SLIP / TRANSACTION RECORD)</span>
        </div>

        <div style="display:flex;justify-content:space-between;margin:2px 0;font-size:11.5px;"><span>Bill No:</span><b>${invoiceNo}</b></div>
        <div style="display:flex;justify-content:space-between;margin:2px 0;font-size:11.5px;"><span>Date &amp; Time:</span><span>${date} ${time}</span></div>
        <div style="display:flex;justify-content:space-between;margin:2px 0;font-size:11.5px;"><span>Cashier:</span><span>${cashier}</span></div>

        <div style="border-top:1px dashed #777;margin:5px 0;"></div>
        <div style="display:flex;justify-content:space-between;margin:2px 0;font-size:11.5px;"><span>Customer:</span><b>${customer}</b></div>
        ${vehicle ? `<div style="display:flex;justify-content:space-between;margin:2px 0;font-size:11.5px;"><span>Vehicle:</span><b>${vehicle}</b></div>` : ''}

        <div style="border-top:1.5px solid #000;margin:6px 0;"></div>
        <div style="font-weight:800;font-size:11px;margin-bottom:2px;">ITEMS SOLD / SERVICES</div>
        <table style="width:100%;border-collapse:collapse;margin:4px 0;">
          <thead>
            <tr>
              <th style="border-bottom:1px dashed #000;padding:3px 0;font-size:10.5px;text-align:left;font-weight:700;">DESCRIPTION</th>
              <th style="border-bottom:1px dashed #000;padding:3px 0;font-size:10.5px;text-align:right;font-weight:700;">AMOUNT</th>
            </tr>
          </thead>
          <tbody>
            ${itemsRows}
          </tbody>
        </table>

        ${discountAmount ? `<div style="border-top:1px dashed #777;margin:4px 0;"></div><div style="display:flex;justify-content:space-between;margin:2px 0;font-size:11.5px;"><span>Discount:</span><span>-${discountAmount}</span></div>` : ''}

        <div style="border-top:1.5px solid #000;margin:6px 0;"></div>
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:16px;font-weight:900;color:#000;padding:3px 0;">
          <span>TOTAL:</span>
          <span>${totalAmount}</span>
        </div>
        <div style="border-top:1px dashed #777;margin:5px 0;"></div>

        <div style="display:flex;justify-content:space-between;margin:2px 0;font-size:11.5px;"><span>Payment Method:</span><b>${paymentMethod}</b></div>
        ${paidAmount ? `<div style="display:flex;justify-content:space-between;margin:2px 0;font-size:11.5px;"><span>Amount Tendered:</span><span>${paidAmount}</span></div>` : ''}
        ${changeAmount ? `<div style="display:flex;justify-content:space-between;margin:2px 0;font-size:11.5px;"><span>Change Due:</span><b style="font-size:13px;">${changeAmount}</b></div>` : ''}

        ${remarks ? `<div style="border-top:1px dashed #777;margin:5px 0;"></div><div style="display:flex;justify-content:space-between;margin:2px 0;font-size:11.5px;"><span>Remarks:</span><span>${remarks}</span></div>` : ''}

        <div style="border-top:1px dashed #777;margin:5px 0;"></div>
        <div style="margin:6px 0;padding:4px 6px;border:1.5px dashed #000;text-align:center;font-weight:800;font-size:10.5px;color:#000;background:#f9f9f9;">
          *** THIS IS NOT AN OFFICIAL RECEIPT ***
        </div>
        <div style="text-align:center;font-size:10px;color:#444;margin-top:6px;line-height:1.3;">
          Thank you for choosing ${company}!<br>
          Please keep this slip for your reference.
        </div>
      </div>
    `;

    let printContainer = document.getElementById("vpos-direct-print-area");
    if (!printContainer) {
      printContainer = document.createElement("div");
      printContainer.id = "vpos-direct-print-area";
      document.body.appendChild(printContainer);
    }
    printContainer.innerHTML = receiptMarkup;

    try {
      window.print();
    } catch (e) {
      console.warn("Direct window.print failed, attempting popup window...", e);
      this.openPrintWindow(receiptMarkup);
    }
  },

  openPrintWindow(receiptMarkup) {
    const w = window.open("", "_blank", "width=420,height=680,menubar=no,toolbar=no,location=no,status=no");
    if (w) {
      w.document.open();
      w.document.write(`<!DOCTYPE html><html><head><meta charset="utf-8"><title>Receipt</title><style>@page{size:80mm auto;margin:0;}body{margin:0;padding:4mm 3mm;background:#fff;color:#000;font-family:-apple-system,sans-serif;}</style></head><body>${receiptMarkup}</body></html>`);
      w.document.close();
      w.focus();
      setTimeout(() => { w.print(); }, 250);
    } else {
      alert("Popup blocked. Please allow popups or use direct Print.");
    }
  },

  initTip() {
    const tip = document.createElement("div");
    tip.className = "vpos-tip";
    document.body.appendChild(tip);
    this._tip = tip;
    const grid = document.getElementById("vpos-products");
    if (!grid) return;
    grid.addEventListener("mouseover", e => {
      const c = e.target.closest("[data-tip]");
      if (c && c.getAttribute("data-tip")) {
        tip.innerHTML = c.getAttribute("data-tip").replace(/&/g, "&amp;").replace(/\n/g, "<br>").replace(/(bin [^\n<]+)/g, "<b>$1</b>");
        tip.style.display = "block";
        tip.style.opacity = "1";
      }
    });
    grid.addEventListener("mousemove", e => {
      let x = e.clientX + 14, y = e.clientY + 14;
      if (x + tip.offsetWidth > window.innerWidth) x = window.innerWidth - tip.offsetWidth - 8;
      if (y + tip.offsetHeight > window.innerHeight) y = window.innerHeight - tip.offsetHeight - 8;
      tip.style.left = x + "px";
      tip.style.top = y + "px";
    });
    grid.addEventListener("mouseout", e => {
      if (e.target.closest("[data-tip]")) {
        tip.style.opacity = "0";
        tip.style.display = "none";
      }
    });
  }
};

window.addEventListener("DOMContentLoaded", () => {
  try { POS.init(); } catch (err) {
    console.error(err);
    document.getElementById("vpos-root").innerHTML = '<div style="padding:24px;color:#b91c1c">POS failed: ' + (err && err.message ? err.message : err) + '</div>';
  }
});
