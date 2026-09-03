import json, urllib.request, urllib.parse

html_path = r'c:\Users\josem\erpnext-system\vps_migration\current_pos_terminal.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_submit = """  async submit(tot, paid) {
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
      alert("✅ POS Invoice " + r.name + " (" + (r.payment_method || payload.payment_method) + ") created successfully!");
      this._recentSale = {
        company: this.company || "",
        cashier: this.cashier || this.user || "Cashier",
        date: new Date().toLocaleDateString("en-PH", { weekday: "long", year: "numeric", month: "long", day: "numeric" }),
        time: new Date().toLocaleTimeString("en-PH", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        invoice_no: r.name,
        vehicle: this.vehicle || "",
        customer: this.customer || "",
        customer_name: this._customerLabel() || "",
        payment_method: this.payment_method || "Cash",
        paid_amount: paid,
        change_amount: paid - tot,
        total_amount: tot,
        discount_amount: 0,
        items_html: this.cart.map(c => `<div class="vpos-receipt-item"><span class="vpos-receipt-item-q">${c.qty} × ${c.item_name}</span><span class="vpos-receipt-item-a">${peso(c.qty * c.rate - c.discount_amount)}</span></div>`).join(""),
        remarks: remarks
      };
      this.clear();
      await this.fetchHistory();
      window.open("/desk#Form/POS Invoice/" + encodeURIComponent(r.name), "_blank");
      // Auto-print the receipt after a short delay so the alert dialog is dismissed first
      setTimeout(() => { this.printReceipt(this._recentSale); }, 800);
    } else {
      const err = api.lastError || "Unknown server response. Please verify in console.";
      alert("⚠️ Failed to create invoice:\\n" + err);
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
      const savedItemsHtml = this.cart.map(c => `<div class="vpos-receipt-item"><span class="vpos-receipt-item-q">${c.qty} × ${c.item_name}</span><span class="vpos-receipt-item-a">${peso(c.qty * c.rate - c.discount_amount)}</span></div>`).join("");
      this._recentSale = {
        company: this.company || "",
        cashier: this.empName || this.cashier || this.user || "Cashier",
        date: new Date().toLocaleDateString("en-PH", { weekday: "long", year: "numeric", month: "long", day: "numeric" }),
        time: new Date().toLocaleTimeString("en-PH", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        invoice_no: r.name,
        vehicle: this.vehicle || "",
        vehicle_name: this._vehicleLabel ? this._vehicleLabel() : "",
        customer: this.customer || "",
        customer_name: this._customerLabel ? this._customerLabel() : "",
        payment_method: this.payment_method || "Cash",
        paid_amount: paid,
        change_amount: paid - tot,
        total_amount: tot,
        discount_amount: 0,
        items_html: savedItemsHtml,
        remarks: remarks
      };
      this.clear();
      await this.fetchHistory();
      // Show receipt modal immediately
      this.showReceiptModal(this._recentSale);
    } else {
      const err = api.lastError || "Unknown server response. Please verify in console.";
      alert("⚠️ Failed to create invoice:\\n" + err);
    }
  },"""

assert old_submit in content, "old_submit not found in content"
content = content.replace(old_submit, new_submit, 1)

# Write to local file
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Sync to bench app
bench_path = r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\www\pos_terminal.html'
with open(bench_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Deploy to live ERPNext Web Page
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

web_page_url = 'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal'
payload_web = json.dumps({'main_section_html': content}).encode()
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
req = urllib.request.Request(web_page_url, data=payload_web, headers=H, method='PUT')
res = opener.open(req)
print('Deployed submit update to Web Page/vehicle-pos-terminal: HTTP', res.status)
