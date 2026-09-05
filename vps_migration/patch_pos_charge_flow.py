import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

wp = s.get(f'{URL}/api/resource/Web Page/vehicle-pos-terminal').json()
html = wp['data']['main_section_html']

# 1. Improve api() to support POST requests cleanly
old_api_fn = """async function api(method, params) {
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
          const parsed = msgs.map(m => typeof m === "string" ? (JSON.parse(m).message || m) : (m.message || m)).join("\\n");
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
}"""

new_api_fn = """async function api(method, params, httpMethod) {
  let url = "/api/method/" + method;
  const isPost = httpMethod === "POST" || method.includes("create_invoice") || method.includes("open_shift") || method.includes("close_shift") || method.includes("save_");
  
  let fetchOptions = {
    cache: "no-store",
    headers: { "X-Requested-With": "XMLHttpRequest" }
  };
  
  if (isPost) {
    fetchOptions.method = "POST";
    fetchOptions.headers["Content-Type"] = "application/json";
    fetchOptions.body = JSON.stringify(params || {});
  } else {
    fetchOptions.method = "GET";
    const p = Object.assign({}, params || {}, { _: Date.now() });
    const qs = Object.keys(p).map(k => encodeURIComponent(k) + "=" + encodeURIComponent(p[k] == null ? "" : p[k])).join("&");
    if (qs) url += "?" + qs;
  }
  
  try {
    const r = await fetch(url, fetchOptions);
    const j = await r.json();
    if (!r.ok) {
      console.error("API error", method, j);
      let errMsg = j.exception || j.exc || "Server error (" + r.status + ")";
      if (j._server_messages) {
        try {
          const msgs = JSON.parse(j._server_messages);
          const parsed = msgs.map(m => typeof m === "string" ? (JSON.parse(m).message || m) : (m.message || m)).join("\\n");
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
}"""

if old_api_fn in html:
    html = html.replace(old_api_fn, new_api_fn)
    print("Replaced api() function with POST support")

# 2. Improve onVeh to not block checkout if vehicle is not linked
old_onveh = """  async onVeh(vehicle) {
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
  },"""

new_onveh = """  async onVeh(vehicle) {
    this.vehicle = vehicle ? String(vehicle).trim() : null;
    const disp = document.querySelector(".vpos-cust");
    if (!this.vehicle) {
      if (!this.customer) this.customer = "Cash Customer";
      if (disp) disp.textContent = "Cash Customer";
      this.totals();
      return;
    }
    const d = await api("vm_pos_vehicle_customer", { vehicle: this.vehicle });
    if (d && d.customer) {
      this.customer = d.customer;
      if (disp) disp.textContent = d.customer_name ? (d.customer + " — " + d.customer_name) : d.customer;
    } else {
      if (!this.customer) this.customer = "Cash Customer";
      if (disp) disp.textContent = this.customer;
    }
    this.totals();
  },"""

if old_onveh in html:
    html = html.replace(old_onveh, new_onveh)
    print("Replaced onVeh() function")

# 3. Improve totals() chargeBtn disabled logic
old_totals_btn = """    const chargeBtn = document.querySelector(".vpos-charge");
    if (chargeBtn) {
      chargeBtn.disabled = !(this.cart.length && this.vehicle && this.customer && this.company && paid >= tot);
    }"""

new_totals_btn = """    const chargeBtn = document.querySelector(".vpos-charge");
    if (chargeBtn) {
      chargeBtn.disabled = !(this.cart.length && paid >= tot);
    }"""

if old_totals_btn in html:
    html = html.replace(old_totals_btn, new_totals_btn)
    print("Replaced totals() button disabled condition")

# 4. Improve charge() to auto-detect vehicle/customer from inputs
old_charge = """  charge() {
    const tot = this.total || 0;
    const paid = flt(document.querySelector(".vpos-paid").value) || 0;
    if (!this.cart.length) { alert("Cart is empty."); return; }
    if (!this.vehicle) { alert("Select a Customer Vehicle."); return; }
    if (!this.customer) { alert("Customer Vehicle has no linked Customer."); return; }
    if (!this.company) { alert("Company not set."); return; }
    if (paid < tot) { alert("Paid amount is less than total."); return; }
    if (!confirm("Charge " + peso(tot) + " (Change: " + peso(paid - tot) + ")?")) return;
    this.submit(tot, paid);
  },"""

new_charge = """  charge() {
    const tot = this.total || 0;
    const pInp = document.querySelector(".vpos-paid");
    const paid = flt(pInp ? pInp.value : 0) || 0;
    
    const vInp = document.querySelector(".vpos-vin");
    if (vInp && vInp.value && !this.vehicle) {
      this.vehicle = vInp.value.trim();
    }
    
    if (!this.customer) {
      const cDisp = document.querySelector(".vpos-cust");
      this.customer = (cDisp && cDisp.textContent.trim()) ? cDisp.textContent.trim() : "Cash Customer";
    }
    if (!this.company) {
      this.company = "ULTRA MRF";
    }
    
    if (!this.cart.length) { alert("Cart is empty."); return; }
    if (paid < tot) { alert("Paid amount is less than total (₱" + peso(tot) + "). Tap paid amount or quick cash to tender."); return; }
    if (!confirm("Confirm Transaction: Charge " + peso(tot) + " (Tendered: " + peso(paid) + " · Change: " + peso(paid - tot) + ")?")) return;
    this.submit(tot, paid);
  },"""

if old_charge in html:
    html = html.replace(old_charge, new_charge)
    print("Replaced charge() function")

# 5. Save updated Web Page
res = s.put(f'{URL}/api/resource/Web Page/vehicle-pos-terminal', json={'main_section_html': html})
print("Web Page update HTTP status:", res.status_code)
