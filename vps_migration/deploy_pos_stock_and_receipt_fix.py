import json, urllib.request, urllib.parse, re

# 1. Read current HTML
html_path = r'c:\Users\josem\erpnext-system\vps_migration\current_pos_terminal.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace loadStock method
old_load_stock = """  async loadStock(list) {
    if (!list || !list.length) return;
    const codes = list.map(it => it.code).join(",");
    const data = await api("vehicle_management.vehicle_management.pos_api.get_stock", { codes: codes }) || {};
    this.STOCK = data;
    list.forEach(it => {
      const el = document.querySelector('[data-code="' + CSS.escape(it.code) + '"]');
      if (!el) return;
      const st = data[it.code];
      const stockEl = el.querySelector(".vpos-card-stock");
      if (stockEl) {
        const s = flt(st ? st.stock : 0);
        stockEl.textContent = "Stock: " + s;
        if (s <= 0) stockEl.classList.add("zero");
      }
      if (st) el.setAttribute("data-tip", this.stockTip(st));
    });
  },"""

new_load_stock = """  async loadStock(list) {
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
  },"""

if old_load_stock in content:
    content = content.replace(old_load_stock, new_load_stock, 1)
    print("Replaced loadStock.")
else:
    print("loadStock pattern not matched directly, using regex...")
    content = re.sub(r'async loadStock\(list\)\s*\{[\s\S]*?if \(st\) el\.setAttribute\("data-tip", this\.stockTip\(st\)\);\s*\}\s*\},', new_load_stock, content)

# Replace totals method to update printBtn.disabled
old_totals_end = """    const chargeBtn = document.querySelector(".vpos-charge");
    if (chargeBtn) {
      chargeBtn.disabled = !(this.cart.length && this.vehicle && this.customer && this.company && paid >= tot);
    }"""

new_totals_end = """    const chargeBtn = document.querySelector(".vpos-charge");
    if (chargeBtn) {
      chargeBtn.disabled = !(this.cart.length && this.vehicle && this.customer && this.company && paid >= tot);
    }
    const printBtn = document.querySelector("#vpos-print-btn");
    if (printBtn) {
      printBtn.disabled = !(this.cart.length || this._recentSale);
    }"""

if old_totals_end in content:
    content = content.replace(old_totals_end, new_totals_end, 1)
    print("Updated totals with printBtn.")

# Replace printReceipt and submit methods
old_print_section = """  /* ── Print Receipt ─────────────────────────────────────────────────────── */
  // Covers all four requested behaviors:
  //   (1) Paper-receipt print via window.print() — print-friendly receipt layout
  //   (2) Print-preview of sold items/receipt — same window.print() opens browser print dialog
  //   (3) Print current open-cart sold-items list — minimal receipt (open cart, no invoice number)
  //   (4) Re-print a completed sale from history — last created invoice cached in _recentSale
  _recentSale: null,

  printReceipt(sale) {
    if (!sale) {
      if (this._recentSale) {
        sale = this._recentSale;
      } else if (this.cart.length) {
        sale = this._buildOpenCartSale();
      } else {
        alert("Nothing to print — cart is empty and no recent sale is available.");
        return;
      }
    }
    const receipt = this._buildReceiptDom(sale);
    receipt.style.position = "fixed";
    receipt.style.left = "0";
    receipt.style.top = "0";
    receipt.style.width = "100%";
    receipt.style.minHeight = "100vh";
    receipt.style.padding = "16mm 14mm";
    receipt.style.background = "#fff";
    receipt.style.color = "#0c1a18";
    receipt.style.boxSizing = "border-box";
    receipt.style.overflow = "hidden";
    receipt.style.zIndex = "9999";
    document.body.appendChild(receipt);
    window.print();
    setTimeout(() => { if (receipt.parentNode) receipt.parentNode.removeChild(receipt); }, 500);
  },"""

new_print_section = """  /* ── Interactive Receipt Modal & Printing ──────────────────────────────── */
  _recentSale: null,

  showReceiptModal(sale) {
    if (!sale) {
      if (this._recentSale) sale = this._recentSale;
      else if (this.cart.length) sale = this._buildOpenCartSale();
      else { alert("No recent sale or cart items to display."); return; }
    }
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
          <span>🧾 POS Official Receipt</span>
          <button class="vpos-receipt-dialog-close" id="vpos-receipt-modal-x">&times;</button>
        </div>
        <div class="vpos-receipt-dialog-body" id="vpos-receipt-modal-body">
        </div>
        <div class="vpos-receipt-dialog-foot">
          <button class="vpos-receipt-btn-print" id="vpos-receipt-modal-print">🖨 Print Receipt</button>
          ${sale.invoice_no && sale.invoice_no !== 'OPEN-CART' ? `<button class="vpos-receipt-btn-desk" onclick="window.open('/desk#Form/POS Invoice/${encodeURIComponent(sale.invoice_no)}', '_blank')">🔗 View Desk</button>` : ''}
          <button class="vpos-receipt-btn-close" id="vpos-receipt-modal-done">Done / Close</button>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);
    overlay.querySelector("#vpos-receipt-modal-body").appendChild(receiptDom);

    overlay.querySelector("#vpos-receipt-modal-x").onclick = () => overlay.remove();
    overlay.querySelector("#vpos-receipt-modal-done").onclick = () => overlay.remove();
    overlay.querySelector("#vpos-receipt-modal-print").onclick = () => {
      self.triggerPrint(receiptDom);
    };
  },

  triggerPrint(receiptDom) {
    const clone = receiptDom.cloneNode(true);
    clone.classList.add("vpos-receipt-printable");
    document.body.appendChild(clone);
    window.print();
    setTimeout(() => { if (clone.parentNode) clone.parentNode.removeChild(clone); }, 600);
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
      itemsHtml += `<div class="vpos-receipt-item"><span class="vpos-receipt-item-q">${it.qty} × ${it.item_name || it.item_code}</span><span class="vpos-receipt-item-a">${peso(it.amount || (it.qty * it.rate))}</span></div>`;
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
      remarks: data.remarks
    };
    this.showReceiptModal(sale);
  },

  printReceipt(sale) {
    this.showReceiptModal(sale);
  },"""

if old_print_section in content:
    content = content.replace(old_print_section, new_print_section, 1)
    print("Replaced printReceipt section.")
else:
    print("old_print_section not found verbatim.")

# Replace submit method
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
      alert("⚠️ Failed to create invoice:\n" + err);
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
      this.showReceiptModal(this._recentSale);
    } else {
      const err = api.lastError || "Unknown server response. Please verify in console.";
      alert("⚠️ Failed to create invoice:\n" + err);
    }
  },"""

if old_submit in content:
    content = content.replace(old_submit, new_submit, 1)
    print("Replaced submit method.")
else:
    print("old_submit not found verbatim.")

# Update history list rendering to add Print Receipt button on each card
old_hist_card_foot = """        <div class="vpos-hist-foot">
          <div class="vpos-hist-amt">${peso(t.total_amount)}</div>
          <div class="vpos-hist-tags">
            <span class="vpos-hist-tag">${t.payment_method || "Cash"}</span>
            <span class="vpos-hist-tag ${isPaid ? 'paid' : ''}">${isPaid ? '✓ Paid' : 'Draft'}</span>
          </div>
        </div>"""

new_hist_card_foot = """        <div class="vpos-hist-foot">
          <div class="vpos-hist-amt">${peso(t.total_amount)}</div>
          <div class="vpos-hist-tags">
            <button class="vpos-hist-print-btn" type="button" onclick="event.stopPropagation(); POS.showReceiptForInvoice('${t.name}')">🖨 Print Receipt</button>
            <span class="vpos-hist-tag">${t.payment_method || "Cash"}</span>
            <span class="vpos-hist-tag ${isPaid ? 'paid' : ''}">${isPaid ? '✓ Paid' : 'Draft'}</span>
          </div>
        </div>"""

if old_hist_card_foot in content:
    content = content.replace(old_hist_card_foot, new_hist_card_foot, 1)
    print("Updated history list card with Print Receipt button.")
else:
    print("old_hist_card_foot not found verbatim.")

# Save modified HTML
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Also sync to bench app file
bench_html = r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\www\pos_terminal.html'
with open(bench_html, 'w', encoding='utf-8') as f:
    f.write(content)

print('Saved HTML files locally.')

# Deploy to live ERPNext Web Page document
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

web_page_url = 'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal'
payload_web = json.dumps({'main_section_html': content}).encode()
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
req = urllib.request.Request(web_page_url, data=payload_web, headers=H, method='PUT')
res = opener.open(req)
print('Deployed to live Web Page/vehicle-pos-terminal: HTTP', res.status)
