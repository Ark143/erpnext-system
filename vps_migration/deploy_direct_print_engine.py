import json, urllib.request, urllib.parse, re

html_path = r'c:\Users\josem\erpnext-system\vps_migration\current_pos_terminal.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Print Stylesheet in CSS
print_css = """
/* ── Direct Page Print Stylesheet: 100% Reliable across all browsers & iframes ── */
@media screen {
  #vpos-direct-print-area {
    display: none !important;
  }
}

@media print {
  @page {
    size: 80mm auto;
    margin: 0;
  }
  html, body {
    margin: 0 !important;
    padding: 0 !important;
    background: #ffffff !important;
    color: #000000 !important;
    width: 80mm !important;
    height: auto !important;
    overflow: visible !important;
  }
  
  /* Force hide every UI element except the dedicated print container */
  #vpos-root, #vpos-receipt-modal-overlay, .vpos-receipt-overlay, .navbar, .web-footer, header, footer, nav, .page-header, .page-breadcrumbs, .modal, .modal-backdrop {
    display: none !important;
    visibility: hidden !important;
  }
  
  #vpos-direct-print-area, #vpos-direct-print-area * {
    visibility: visible !important;
  }
  
  #vpos-direct-print-area {
    display: block !important;
    position: static !important;
    width: 76mm !important;
    max-width: 76mm !important;
    margin: 0 auto !important;
    padding: 3mm 2mm !important;
    box-sizing: border-box !important;
    color: #000000 !important;
    background: #ffffff !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Courier New', monospace !important;
    font-size: 12px !important;
    line-height: 1.35 !important;
    page-break-inside: avoid !important;
    page-break-after: avoid !important;
  }
  
  #vpos-direct-print-area .vpos-receipt-co {
    font-size: 16px !important;
    font-weight: 900 !important;
    text-align: center !important;
    text-transform: uppercase !important;
    color: #000 !important;
  }
  
  #vpos-direct-print-area .vpos-receipt-not-official {
    margin: 6px 0 !important;
    padding: 4px 6px !important;
    border: 1.5px dashed #000 !important;
    text-align: center !important;
    font-weight: 800 !important;
    font-size: 11px !important;
    color: #000 !important;
    background: #fff !important;
  }
  
  #vpos-direct-print-area .vpos-receipt-grand-row {
    font-size: 16px !important;
    font-weight: 900 !important;
    color: #000 !important;
  }
}
"""

# Replace @media print section in content
content = re.sub(r'@media print\s*\{[\s\S]*?\}\s*\}', '', content)
content = re.sub(r'/\* ── Direct Page Print Stylesheet[\s\S]*?\}\s*\}', '', content)

content = content.replace('</style>', print_css + '\n</style>', 1)
print('Replaced print stylesheet.')

# 2. Update print methods to support direct print + popup window
new_print_methods = """  /* ── Triple-Fallback POS Receipt Printing Engine ───────────────────────── */
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

    // Build structured items table
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

    // 1. Inject into direct print container
    let printContainer = document.getElementById("vpos-direct-print-area");
    if (!printContainer) {
      printContainer = document.createElement("div");
      printContainer.id = "vpos-direct-print-area";
      document.body.appendChild(printContainer);
    }
    printContainer.innerHTML = receiptMarkup;

    // 2. Trigger print
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

# Replace previous print methods in content
content = re.sub(r'  /\* ── Clean Isolated Printing[\s\S]*?pFrame\.contentWindow\.print\(\);\s*\}\s*,\s*250\);\s*\},', new_print_methods, content)

# Also update showReceiptModal buttons
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
  },"""

content = re.sub(r'  showReceiptModal\(sale\)\s*\{[\s\S]*?self\.printViaIframe\(sale\);\s*\}\s*;\s*\},', new_show_receipt_modal, content)

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
print('Deployed direct print engine to Web Page: HTTP', res.status)
