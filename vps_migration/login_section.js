async function frappeLogin(usr, pwd) {
  const fd = new URLSearchParams();
  fd.set("usr", usr);
  fd.set("pwd", pwd);
  const r = await fetch("/api/method/login", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded", "Expect": "" }, body: fd.toString() });
  const j = await r.json();
  return j;
}

const POS = {
  cart: [], customer: null, vehicle: null, company: null, payment_method: "Cash", category: null, total: 0, _vt: null,
  PROD_LIMIT: 12, showAll: false, STOCK: {}, onlyStock: false, loggedIn: false, user: null, cashier: null,
  history: [], discount: 0, loggedOutMsg: null, mobileTicketOpen: false,

  async init() {
    this.hideChrome();
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
    window.__vposPwd = null;
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
        this.user = usr; window.__vposPwd = pwd;
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
    this.build();
    this.load();
  },

  openScanner() {
    const v = document.getElementById("vpos-video");
    const err = document.getElementById("vpos-li-err");
    err.textContent = "Point camera at the cashier QR badge...";
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then(stream => {
      v.srcObject = stream; v.style.display = "block"; v.play();
      const canvas = document.createElement("canvas");
      const tick = () => {
