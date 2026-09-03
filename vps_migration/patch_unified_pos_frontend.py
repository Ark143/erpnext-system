import urllib.request, json

with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update submit() to use vm_pos_create_invoice
old_submit = """  async submit(tot, paid) {
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
    });
    if (r && r.name) {
      alert("POS Invoice " + r.name + " created successfully!");
      this.clear();
      this.fetchHistory();
      if (r.pos_invoice) window.open("/desk#Form/POS Invoice/" + r.pos_invoice, "_blank");
    } else {
      alert("Failed to create invoice. See console.");
    }
  },"""

new_submit = """  async submit(tot, paid) {
    const items = this.cart.map(c => ({ item_code: c.item_code, qty: c.qty, rate: c.rate, discount_amount: c.discount_amount, uom: c.uom }));
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
      alert("POS Invoice " + r.name + " created successfully!");
      this.clear();
      this.fetchHistory();
      window.open("/desk#Form/POS Invoice/" + encodeURIComponent(r.name), "_blank");
    } else {
      alert("Failed to create invoice. See console.");
    }
  },"""

html = html.replace(old_submit, new_submit)

# 2. Update fetchHistory() to call vm_pos_history
old_fetch = 'list = await api("vehicle_management.vehicle_management.pos_api.get_history", queryParams) || [];'
new_fetch = 'list = await api("vm_pos_history", queryParams) || [];'
html = html.replace(old_fetch, new_fetch)

# 3. Update load() initial history call
old_load_hist = 'this.history = await api("vehicle_management.vehicle_management.pos_api.get_history") || [];'
new_load_hist = 'this.history = await api("vm_pos_history") || [];'
html = html.replace(old_load_hist, new_load_hist)

# 4. Clean up renderHistoryList card template to directly link POS Invoice
old_card_tpl = """      <div class="vpos-hist-card">
        <div class="vpos-hist-top">
          <div class="vpos-hist-code" onclick="window.open('/desk#Form/Vehicle POS Invoice/${encodeURIComponent(t.name)}', '_blank')" title="Open Vehicle POS Invoice in Desk">${t.name}</div>
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
            <span class="vpos-hist-tag">${t.payment_method || "Cash"}</span>
            <span class="vpos-hist-tag ${isPaid ? 'paid' : ''}">${isPaid ? '✓ Paid' : 'Draft'}</span>
            ${posLink}
          </div>
        </div>
      </div>"""

new_card_tpl = """      <div class="vpos-hist-card">
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
            <span class="vpos-hist-tag">${t.payment_method || "Cash"}</span>
            <span class="vpos-hist-tag ${isPaid ? 'paid' : ''}">${isPaid ? '✓ Paid' : 'Draft'}</span>
          </div>
        </div>
      </div>"""

html = html.replace(old_card_tpl, new_card_tpl)

# Save local copies
with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved local HTML files.")

# Deploy to Web Page/vehicle-pos-terminal
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

save_url = 'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal'
payload = json.dumps({'main_section_html': html}).encode('utf-8')
req = urllib.request.Request(save_url, data=payload, headers={'Content-Type': 'application/json'}, method='PUT')
res = opener.open(req)
print("SUCCESSFULLY deployed updated unified POS terminal! Status:", res.status)
