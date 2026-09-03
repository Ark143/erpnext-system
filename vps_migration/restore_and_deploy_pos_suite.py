import json, urllib.request, urllib.parse, re, subprocess, os

html_path = r'c:\Users\josem\erpnext-system\vps_migration\current_pos_terminal.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Construct the complete and robust POS receipt and submit suite
pos_methods_block = """  /* ── Transaction Submission & Receipt Suite ───────────────────────────── */
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
      alert("⚠️ Failed to create invoice:\n" + err);
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
  },"""

# In current content, replace from `  /* ── Interactive Receipt Modal` or `  /* ── Triple-Fallback` up to `  initTip()`
start_marker = "  /* ── Interactive Receipt Modal"
if start_marker not in content:
    start_marker = "  /* ── Triple-Fallback"

end_marker = "  initTip() {"

idx_start = content.find(start_marker)
idx_end = content.find(end_marker)

assert idx_start != -1, "start_marker not found"
assert idx_end != -1, "end_marker not found"

content = content[:idx_start] + pos_methods_block + "\n\n" + content[idx_end:]

# Save locally
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

bench_path = r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\www\pos_terminal.html'
with open(bench_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Validate all script blocks with Node AST
scripts = re.findall(r'<script\b[^>]*>([\s\S]*?)<\/script>', content, re.I)
for idx, s in enumerate(scripts):
    sf_name = f'c:\\Users\\josem\\erpnext-system\\vps_migration\\script_{idx}.js'
    with open(sf_name, 'w', encoding='utf-8') as sf:
        sf.write(s)
    res = subprocess.run(['node', '-c', sf_name], capture_output=True, text=True)
    if res.returncode != 0:
        print(f'ERROR in script {idx}:', res.stderr)
    else:
        print(f'script_{idx}.js: Syntax OK')
    try:
        os.remove(sf_name)
    except:
        pass

# Deploy to live ERPNext Web Page
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

web_page_url = 'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal'
payload_web = json.dumps({'main_section_html': content}).encode()
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
req = urllib.request.Request(web_page_url, data=payload_web, headers=H, method='PUT')
res = opener.open(req)
print('Deployed complete POS methods suite: HTTP', res.status)
