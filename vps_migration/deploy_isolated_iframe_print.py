import json, urllib.request, urllib.parse, re

html_path = r'c:\Users\josem\erpnext-system\vps_migration\current_pos_terminal.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace triggerPrint and printViaIframe in POS object
new_print_methods = """  /* ── Clean Isolated Printing (Zero CSS Pollution) ──────────────────────── */
  triggerPrint(saleOrDom) {
    const sale = this._currentModalSale || this._recentSale || (this.cart.length ? this._buildOpenCartSale() : null);
    if (sale) {
      this.printViaIframe(sale);
    } else {
      window.print();
    }
  },

  printViaIframe(sale) {
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
    
    // Build clean table rows for items
    let itemsRows = "";
    const itemList = sale.items || sale.items_raw || [];
    if (itemList && itemList.length) {
      itemList.forEach(it => {
        const amt = flt(it.amount || (flt(it.qty) * flt(it.rate)) - flt(it.discount_amount || 0));
        itemsRows += `
          <tr>
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

    const printHtml = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Receipt - ${invoiceNo}</title>
<style>
  @page {
    size: 80mm auto;
    margin: 0;
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Courier New', monospace;
    font-size: 12.5px;
    line-height: 1.4;
    color: #000000;
    background: #ffffff;
    width: 76mm;
    max-width: 76mm;
    margin: 0 auto;
    padding: 4mm 3mm;
  }
  .center { text-align: center; }
  .bold { font-weight: 700; }
  .co-name { font-size: 17px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.5px; }
  .co-sub { font-size: 11px; color: #333; margin-top: 1px; }
  .not-official {
    margin: 8px 0;
    padding: 6px 4px;
    border: 1.5px dashed #000;
    text-align: center;
    font-weight: 800;
    font-size: 11px;
    line-height: 1.3;
    background: #f9f9f9;
  }
  .sep-dash { border-top: 1px dashed #777; margin: 6px 0; }
  .sep-solid { border-top: 1.5px solid #000; margin: 8px 0; }
  .row {
    display: flex;
    justify-content: space-between;
    margin: 2px 0;
    font-size: 12px;
  }
  .row .lbl { color: #444; }
  .row .val { font-weight: 700; text-align: right; }
  .tbl {
    width: 100%;
    border-collapse: collapse;
    margin: 4px 0;
  }
  .tbl th {
    border-bottom: 1px dashed #000;
    padding: 4px 0;
    font-size: 11px;
    text-align: left;
    font-weight: 700;
  }
  .tbl th.r { text-align: right; }
  .grand-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 16px;
    font-weight: 900;
    padding: 4px 0;
  }
  .footer-msg {
    text-align: center;
    font-size: 10.5px;
    color: #444;
    margin-top: 8px;
    line-height: 1.3;
  }
</style>
</head>
<body>
  <div class="center co-name">${company}</div>
  <div class="center co-sub">Vehicle Management System &amp; Services</div>

  <div class="not-official">
    *** THIS IS NOT AN OFFICIAL RECEIPT ***<br>
    <span style="font-size: 9.5px; font-weight: 600;">(ORDER SLIP / TRANSACTION RECORD)</span>
  </div>

  <div class="row"><span class="lbl">Bill No:</span><span class="val">${invoiceNo}</span></div>
  <div class="row"><span class="lbl">Date &amp; Time:</span><span class="val">${date} ${time}</span></div>
  <div class="row"><span class="lbl">Cashier:</span><span class="val">${cashier}</span></div>

  <div class="sep-dash"></div>
  <div class="row"><span class="lbl">Customer:</span><span class="val">${customer}</span></div>
  ${vehicle ? `<div class="row"><span class="lbl">Vehicle:</span><span class="val">${vehicle}</span></div>` : ''}

  <div class="sep-solid"></div>
  <div style="font-weight: 800; font-size: 11.5px; margin-bottom: 2px;">ITEMS SOLD / SERVICES</div>
  <table class="tbl">
    <thead>
      <tr>
        <th>DESCRIPTION</th>
        <th class="r">AMOUNT</th>
      </tr>
    </thead>
    <tbody>
      ${itemsRows}
    </tbody>
  </table>

  ${discountAmount ? `<div class="sep-dash"></div><div class="row"><span class="lbl">Discount:</span><span class="val">-${discountAmount}</span></div>` : ''}

  <div class="sep-solid"></div>
  <div class="grand-row">
    <span>TOTAL:</span>
    <span>${totalAmount}</span>
  </div>
  <div class="sep-dash"></div>

  <div class="row"><span class="lbl">Payment Method:</span><span class="val">${paymentMethod}</span></div>
  ${paidAmount ? `<div class="row"><span class="lbl">Amount Tendered:</span><span class="val">${paidAmount}</span></div>` : ''}
  ${changeAmount ? `<div class="row"><span class="lbl">Change Due:</span><span class="val" style="font-size: 13.5px;">${changeAmount}</span></div>` : ''}

  ${remarks ? `<div class="sep-dash"></div><div class="row"><span class="lbl">Remarks:</span><span class="val">${remarks}</span></div>` : ''}

  <div class="sep-dash"></div>
  <div class="not-official" style="margin-top: 6px;">
    *** THIS IS NOT AN OFFICIAL RECEIPT ***
  </div>
  <div class="footer-msg">
    Thank you for choosing ${company}!<br>
    Please keep this slip for your reference.
  </div>
</body>
</html>`;

    let pFrame = document.getElementById("vpos-print-frame");
    if (!pFrame) {
      pFrame = document.createElement("iframe");
      pFrame.id = "vpos-print-frame";
      pFrame.style.cssText = "position:fixed;right:0;bottom:0;width:1px;height:1px;border:none;opacity:0;pointer-events:none;";
      document.body.appendChild(pFrame);
    }
    
    const doc = pFrame.contentWindow.document;
    doc.open();
    doc.write(printHtml);
    doc.close();

    setTimeout(() => {
      pFrame.contentWindow.focus();
      pFrame.contentWindow.print();
    }, 250);
  },"""

# Update showReceiptModal to save _currentModalSale
new_show_receipt_modal = """  showReceiptModal(sale) {
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
      self.printViaIframe(sale);
    };
  },"""

# Update _buildOpenCartSale to include items array
new_open_cart_sale = """  _buildOpenCartSale() {
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
    const paid = flt(document.querySelector(".vpos-paid").value) || 0;
    const change = paid - total;
    const paymentMethod = this.payment_method || "Cash";
    const cashier = this.empName || this.cashier || this.user || "Cashier";
    const company = this.company || "";
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
  },"""

# Update showReceiptForInvoice
new_show_receipt_for_inv = """  async showReceiptForInvoice(invName) {
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
  },"""

# Replace in content using regex
content = re.sub(r'  showReceiptModal\(sale\)\s*\{[\s\S]*?self\.triggerPrint\(receiptDom\);\s*\}\s*\},', new_show_receipt_modal, content)
content = re.sub(r'  triggerPrint\(receiptDom\)\s*\{[\s\S]*?\}\s*\},', new_print_methods, content)
content = re.sub(r'  _buildOpenCartSale\(\)\s*\{[\s\S]*?remarks:\s*""\s*\}\s*\},', new_open_cart_sale, content)
content = re.sub(r'  async showReceiptForInvoice\(invName\)\s*\{[\s\S]*?this\.showReceiptModal\(sale\);\s*\},', new_show_receipt_for_inv, content)

# Save to local file
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
print('Deployed isolated iframe printing fix to Web Page: HTTP', res.status)
