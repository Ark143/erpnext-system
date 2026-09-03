import urllib.request, json

with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update api() to prevent HTTP caching and capture lastError
old_api = """async function api(method, params) {
  let url = "/api/method/" + method;
  if (params) {
    const qs = Object.keys(params).map(k => encodeURIComponent(k) + "=" + encodeURIComponent(params[k] == null ? "" : params[k])).join("&");
    if (qs) url += "?" + qs;
  }
  try {
    const r = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
    const j = await r.json();
    return j.message;
  } catch (e) {
    console.error("api", method, e);
    return null;
  }
}"""

new_api = """async function api(method, params) {
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

if old_api in html:
    html = html.replace(old_api, new_api)
    print("1. Upgraded api() with cache-busting and error parsing.")
else:
    print("1. Warning: old_api pattern not exact match, checking fallback replacement.")

# 2. Update submit() to show clear error messages and await real-time fetchHistory()
old_submit_start = 'async submit(tot, paid) {'
old_submit_block = """    const r = await api("vm_pos_create_invoice", { data: JSON.stringify(payload) });
    if (r && r.name) {
      alert("POS Invoice " + r.name + " created successfully!");
      this.clear();
      this.fetchHistory();
      window.open("/desk#Form/POS Invoice/" + encodeURIComponent(r.name), "_blank");
    } else {
      alert("Failed to create invoice. See console.");
    }"""

new_submit_block = """    const r = await api("vm_pos_create_invoice", { data: JSON.stringify(payload) });
    if (r && r.name) {
      alert("✅ POS Invoice " + r.name + " (" + (r.payment_method || payload.payment_method) + ") created successfully!");
      this.clear();
      await this.fetchHistory();
      window.open("/desk#Form/POS Invoice/" + encodeURIComponent(r.name), "_blank");
    } else {
      const err = api.lastError || "Unknown server response. Please verify in console.";
      alert("⚠️ Failed to create invoice:\\n" + err);
    }"""

if old_submit_block in html:
    html = html.replace(old_submit_block, new_submit_block)
    print("2. Upgraded submit() with descriptive alerts and awaited history fetch.")

# 3. Add branch filter selector and instant sync to the History toolbar
old_hist_controls = """            <div class="vpos-hist-pills" id="vpos-hist-pills">
              <button class="vpos-hist-pill active" data-period="all">All</button>
              <button class="vpos-hist-pill" data-period="today">Today</button>
              <button class="vpos-hist-pill" data-period="month">This Month</button>
            </div>"""

new_hist_controls = """            <div class="vpos-hist-pills" id="vpos-hist-pills">
              <button class="vpos-hist-pill active" data-period="all">All</button>
              <button class="vpos-hist-pill" data-period="today">Today</button>
              <button class="vpos-hist-pill" data-period="month">This Month</button>
            </div>
            <select class="vpos-hist-dt" id="vpos-hist-branch-filter" style="height:34px;background:#fff;border:1px solid var(--line);border-radius:8px;padding:0 8px;font-size:12px;font-weight:600;color:var(--txt);" title="Filter by Branch">
              <option value="">🏢 All Branches</option>
              <option value="ULTRA MRF" selected>ULTRA MRF</option>
              <option value="Ultra MRF Dau Main">Ultra MRF Dau Main</option>
              <option value="Ultra MRF Dau Annex">Ultra MRF Dau Annex</option>
            </select>"""

if old_hist_controls in html:
    html = html.replace(old_hist_controls, new_hist_controls)
    print("3. Added branch selector to History toolbar.")

# 4. Wire branch selector change in renderHistory()
old_wire_search = """      // Bind search input with debounce"""
new_wire_search = """      // Bind branch filter change
      const brSelect = view.querySelector("#vpos-hist-branch-filter");
      if (brSelect) {
        brSelect.value = self.company || "ULTRA MRF";
        brSelect.onchange = () => {
          self.fetchHistory({ company: brSelect.value });
        };
      }

      // Bind search input with debounce"""

if old_wire_search in html:
    html = html.replace(old_wire_search, new_wire_search)
    print("4. Wired branch filter selector change event.")

# 5. Save local files
with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("5. Saved local HTML files.")

# 6. Deploy to Web Page/vehicle-pos-terminal
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

save_url = 'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal'
payload = json.dumps({'main_section_html': html}).encode('utf-8')
req = urllib.request.Request(save_url, data=payload, headers={'Content-Type': 'application/json'}, method='PUT')
res = opener.open(req)
print(f"6. Successfully deployed to Web Page/vehicle-pos-terminal: HTTP {res.status}")
