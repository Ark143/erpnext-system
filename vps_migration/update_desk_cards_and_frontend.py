import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# ─────────────────────────────────────────────────────────────────────────────
# 1. Update Desk Number Cards & Dashboard Charts to use POS Invoice
# ─────────────────────────────────────────────────────────────────────────────
print("--- Updating Desk Number Cards & Charts ---")
try:
    req = urllib.request.Request(
        'http://38.247.138.224:10017/api/resource/Number%20Card/' + urllib.parse.quote('Vehicle POS Invoices Count'),
        data=json.dumps({
            'document_type': 'POS Invoice',
            'function': 'Count'
        }).encode(),
        headers={'Content-Type': 'application/json'},
        method='PUT'
    )
    res = opener.open(req)
    print("  Updated 'Vehicle POS Invoices Count' -> POS Invoice:", res.status)
except Exception as e:
    print("  Error updating Number Card:", e)

try:
    req = urllib.request.Request(
        'http://38.247.138.224:10017/api/resource/Dashboard%20Chart/' + urllib.parse.quote('Vehicle POS Sales by Company'),
        data=json.dumps({
            'document_type': 'POS Invoice',
            'aggregate_function_based_on': 'grand_total',
            'group_by_based_on': 'company'
        }).encode(),
        headers={'Content-Type': 'application/json'},
        method='PUT'
    )
    res = opener.open(req)
    print("  Updated 'Vehicle POS Sales by Company' -> POS Invoice (grand_total):", res.status)
except Exception as e:
    print("  Error updating Dashboard Chart:", e)

# ─────────────────────────────────────────────────────────────────────────────
# 2. Update current_pos_terminal.html
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Patching current_pos_terminal.html ---")
with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# A. Auto-login on init() if already authenticated in Desk/Browser
old_init = """  async init() {
    this.hideChrome();
    this.buildLogin();
  },"""

new_init = """  async init() {
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
  },"""

if old_init in html:
    html = html.replace(old_init, new_init)
    print("  [A] Injected session auto-detection in init()")
else:
    print("  [A] Note: old_init pattern differed, checking if already injected")

# B. Robust company defaulting in load()
old_comp = """    // Ensure company is set from cashier employee record or first meta company
    if (!this.company && meta && meta.companies && meta.companies.length) {
      this.company = meta.companies[0];
    }"""

new_comp = """    // Ensure company is set from cashier employee record or default to ULTRA MRF
    if (!this.company) {
      this.company = "ULTRA MRF";
    }"""

if old_comp in html:
    html = html.replace(old_comp, new_comp)
    print("  [B] Fixed company fallback from meta.companies[0] to 'ULTRA MRF'")
else:
    print("  [B] Note: old_comp pattern not found or already changed")

# C. Robust fetchHistory queryParams: if company is 'All Branches', pass empty string
old_fetch_qp = """    const queryParams = {
      period: this.histPeriod,
      from_date: this.histFromDate,
      to_date: this.histToDate,
      search: this.histSearch,
      company: this.company || ""
    };"""

new_fetch_qp = """    const histCo = (this.company === "All Branches" || !this.company) ? "" : this.company;
    const queryParams = {
      period: this.histPeriod,
      from_date: this.histFromDate,
      to_date: this.histToDate,
      search: this.histSearch,
      company: histCo
    };"""

if old_fetch_qp in html:
    html = html.replace(old_fetch_qp, new_fetch_qp)
    print("  [C] Updated fetchHistory queryParams company filter")
else:
    print("  [C] Note: old_fetch_qp pattern differed")

# D. Save local files
with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("  Local HTML files saved.")

# E. Deploy to Web Page/vehicle-pos-terminal
save_url = 'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal'
payload = json.dumps({'main_section_html': html}).encode('utf-8')
req = urllib.request.Request(save_url, data=payload, headers={'Content-Type': 'application/json'}, method='PUT')
res = opener.open(req)
print(f"  SUCCESS! Deployed to Web Page/vehicle-pos-terminal: HTTP {res.status}")
