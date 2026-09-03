import json, urllib.request, urllib.parse, re

html_path = r'c:\Users\josem\erpnext-system\vps_migration\current_pos_terminal.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CSS for Receipt Modal and Thermal/Standard Printing
enhanced_receipt_css = """
/* ── High Legibility, Crisp POS Receipt Modal & Thermal / Standard Print Layout ── */
.vpos-receipt-overlay {
  position: fixed;
  inset: 0;
  background: rgba(12, 26, 24, 0.82);
  backdrop-filter: blur(5px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.vpos-receipt-dialog {
  background: #ffffff;
  color: #111827;
  border-radius: 18px;
  width: 100%;
  max-width: 520px;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}
.vpos-receipt-dialog-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  font-family: var(--font-head, -apple-system, BlinkMacSystemFont, sans-serif);
  font-weight: 800;
  font-size: 16px;
  color: #0f172a;
}
.vpos-receipt-dialog-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #64748b;
  line-height: 1;
  padding: 4px;
  border-radius: 6px;
}
.vpos-receipt-dialog-close:hover {
  background: #e2e8f0;
  color: #0f172a;
}
.vpos-receipt-dialog-body {
  padding: 24px 28px;
  overflow-y: auto;
  flex: 1;
  background: #ffffff;
}
.vpos-receipt-dialog-foot {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}
.vpos-receipt-btn-print {
  flex: 2;
  background: #10b981;
  color: #ffffff;
  border: none;
  border-radius: 12px;
  padding: 14px 20px;
  font-weight: 800;
  font-size: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3);
  transition: all 0.15s ease;
}
.vpos-receipt-btn-print:hover {
  background: #059669;
  transform: translateY(-1px);
}
.vpos-receipt-btn-desk {
  background: #e2e8f0;
  color: #1e293b;
  border: none;
  border-radius: 12px;
  padding: 14px 16px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
}
.vpos-receipt-btn-desk:hover {
  background: #cbd5e1;
}
.vpos-receipt-btn-close {
  flex: 1;
  background: #e2e8f0;
  color: #1e293b;
  border: none;
  border-radius: 12px;
  padding: 14px 16px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
}
.vpos-receipt-btn-close:hover {
  background: #cbd5e1;
}

/* ── Receipt Content Inside Box ── */
.vpos-receipt-box {
  width: 100%;
  max-width: 440px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Courier New', monospace;
  font-size: 13.5px;
  line-height: 1.5;
  color: #111827;
  background: #ffffff;
}

.vpos-receipt-co {
  font-size: 20px;
  font-weight: 900;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #0f172a;
}

.vpos-receipt-sub {
  font-size: 12px;
  text-align: center;
  color: #475569;
  margin-top: 2px;
  font-weight: 500;
}

.vpos-receipt-not-official {
  margin: 12px 0;
  padding: 8px 10px;
  border: 1.5px dashed #dc2626;
  background: #fef2f2;
  text-align: center;
  font-weight: 800;
  font-size: 13px;
  letter-spacing: 0.5px;
  color: #b91c1c;
  border-radius: 6px;
}

.vpos-receipt-sep {
  border-top: 1px dashed #cbd5e1;
  margin: 10px 0;
}

.vpos-receipt-sep-solid {
  border-top: 2px solid #0f172a;
  margin: 12px 0;
}

.vpos-receipt-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin: 4px 0;
  font-size: 13.5px;
}

.vpos-receipt-row span:first-child {
  color: #475569;
}

.vpos-receipt-row b, .vpos-receipt-row span:last-child {
  color: #0f172a;
  font-weight: 700;
  text-align: right;
}

.vpos-receipt-item-block {
  margin: 8px 0;
  padding: 6px 0;
  border-bottom: 1px dashed #e2e8f0;
}
.vpos-receipt-item-block:last-child {
  border-bottom: none;
}

.vpos-receipt-item-header {
  display: flex;
  justify-content: space-between;
  font-weight: 700;
  font-size: 14px;
  color: #0f172a;
}

.vpos-receipt-item-sub {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.vpos-receipt-grand-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 20px;
  font-weight: 900;
  color: #0f172a;
  padding: 6px 0;
}

.vpos-receipt-foot-msg {
  text-align: center;
  font-size: 11.5px;
  color: #64748b;
  margin-top: 12px;
  line-height: 1.4;
}

/* ── Print Stylesheet: Crisp, Standard 1-Page Thermal or Full Sheet ── */
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
  body * {
    visibility: hidden !important;
  }
  .vpos-receipt-printable, .vpos-receipt-printable * {
    visibility: visible !important;
  }
  .vpos-receipt-printable {
    position: absolute !important;
    left: 0 !important;
    top: 0 !important;
    width: 78mm !important;
    max-width: 78mm !important;
    padding: 3mm 2mm !important;
    margin: 0 auto !important;
    box-sizing: border-box !important;
    box-shadow: none !important;
    border: none !important;
    font-family: monospace, sans-serif !important;
    font-size: 12.5px !important;
    line-height: 1.35 !important;
    color: #000000 !important;
    page-break-inside: avoid !important;
    page-break-after: avoid !important;
  }
  .vpos-receipt-printable .vpos-receipt-co {
    font-size: 17px !important;
  }
  .vpos-receipt-printable .vpos-receipt-grand-row {
    font-size: 18px !important;
  }
}
"""

# Replace the previous receipt styling in content
content = re.sub(r'/\* ── Standard 1-Page Thermal POS Receipt Layout[\s\S]*?/\* ── Print Stylesheet', '', content)
content = re.sub(r'/\* ── High Legibility, Crisp POS Receipt Modal[\s\S]*?/\* ── Print Stylesheet', '', content)

if '/* ── High Legibility, Crisp POS Receipt Modal' not in content:
    content = content.replace('</style>', enhanced_receipt_css + '\n</style>', 1)
    print('Updated CSS with high-legibility styling.')

# 2. Update _buildReceiptDom and build items cleanly
new_build_receipt = """  _buildReceiptDom(sale) {
    const peso = v => "₱ " + parseFloat(v || 0).toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const company = sale.company || "ULTRA MRF";
    const cashier = sale.cashier || "Cashier";
    const date = sale.date || "";
    const time = sale.time || "";
    const invoiceNo = sale.invoice_no || "POS-0000";
    const vehicle = sale.vehicle ? (sale.vehicle + (sale.vehicle_name ? (" — " + sale.vehicle_name) : "")) : "";
    const customer = sale.customer_name ? (sale.customer + " — " + sale.customer_name) : (sale.customer || "");
    const paymentMethod = sale.payment_method || "Cash";
    const paidAmount = sale.paid_amount != null ? peso(sale.paid_amount) : "";
    const changeAmount = sale.change_amount != null ? peso(sale.change_amount) : "";
    const totalAmount = sale.total_amount != null ? peso(sale.total_amount) : "";
    const discountAmount = sale.discount_amount != null && parseFloat(sale.discount_amount) > 0 ? peso(sale.discount_amount) : "";
    const remarks = sale.remarks ? sale.remarks : "";
    const itemsHtml = sale.items_html || "";

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
        <div class="vpos-receipt-items-container">${itemsHtml || '<div style="color:#64748b;font-style:italic;">No items.</div>'}</div>

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
  },"""

content = re.sub(r'  _buildReceiptDom\(sale\)\s*\{[\s\S]*?return div;\s*\},', new_build_receipt, content)
print('Updated _buildReceiptDom with large, crisp typography.')

# Update item formatting in submit, _buildOpenCartSale, and showReceiptForInvoice
old_open_cart_items = """    this.cart.forEach(c => {
      const amt = flt(c.qty) * flt(c.rate) - flt(c.discount_amount);
      total += amt;
      items += `<div class="vpos-receipt-item"><span class="vpos-receipt-item-q">${c.qty} × ${c.item_name}</span><span class="vpos-receipt-item-a">${peso(amt)}</span></div>`;
    });"""

new_open_cart_items = """    this.cart.forEach(c => {
      const amt = flt(c.qty) * flt(c.rate) - flt(c.discount_amount);
      total += amt;
      items += `
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
    });"""

if old_open_cart_items in content:
    content = content.replace(old_open_cart_items, new_open_cart_items, 1)
    print("Updated _buildOpenCartSale item layout.")

# Save modified HTML locally
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

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
print('Deployed enlarged receipt layout to Web Page/vehicle-pos-terminal: HTTP', res.status)
