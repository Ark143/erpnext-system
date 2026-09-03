import json, urllib.request, urllib.parse, re

html_path = r'c:\Users\josem\erpnext-system\vps_migration\current_pos_terminal.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CSS: hide all Frappe website default header, navbar, footer, breadcrumbs
css_to_add_or_replace = """
/* ── Aggressively Hide ERPNext Default Website Header, Navbar, Footer, Breadcrumbs ── */
header, footer, nav, .navbar, .web-footer, .page-header, .page-breadcrumbs, .footer-powered, .page-head, .page-footer, .standard-sidebar, .page-sidebar, .sidebar-column, .web-footer-powered {
  display: none !important;
  visibility: hidden !important;
  height: 0 !important;
  max-height: 0 !important;
  min-height: 0 !important;
  overflow: hidden !important;
  margin: 0 !important;
  padding: 0 !important;
  border: none !important;
  opacity: 0 !important;
  pointer-events: none !important;
}

body, html {
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
  width: 100vw !important;
  height: 100vh !important;
  max-width: 100vw !important;
  max-height: 100vh !important;
  background: #0c1a18 !important;
}

.page-content-wrapper, .page-container, #page-vehicle-pos-terminal, .main-column, .container {
  margin: 0 !important;
  padding: 0 !important;
  max-width: 100vw !important;
  width: 100vw !important;
  height: 100vh !important;
}

/* ── Standard 1-Page Thermal POS Receipt Layout (80mm & Screen) ── */
.vpos-receipt {
  width: 100%;
  max-width: 330px;
  margin: 0 auto;
  font-family: 'Courier New', Courier, monospace;
  font-size: 11.5px;
  line-height: 1.35;
  color: #000;
  background: #fff;
  padding: 12px 14px;
  box-sizing: border-box;
}

.vpos-receipt-co {
  font-family: var(--font-head, sans-serif);
  font-size: 16px;
  font-weight: 800;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #0c1a18;
}

.vpos-receipt-sub {
  font-size: 10.5px;
  text-align: center;
  color: #444;
  margin-top: 1px;
}

.vpos-receipt-not-official {
  margin: 7px 0;
  padding: 4px 6px;
  border-top: 1px dashed #000;
  border-bottom: 1px dashed #000;
  text-align: center;
  font-weight: 800;
  font-size: 10.5px;
  letter-spacing: 0.5px;
  color: #000;
  background: #f8f8f8;
}

.vpos-receipt-sep {
  border-top: 1px dashed #555;
  margin: 6px 0;
}

.vpos-receipt-sep-solid {
  border-top: 1.5px solid #000;
  margin: 7px 0;
}

.vpos-receipt-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin: 2px 0;
  font-size: 11px;
}

.vpos-receipt-row b {
  color: #000;
  font-weight: 700;
}

.vpos-receipt-tbl {
  width: 100%;
  border-collapse: collapse;
  margin: 5px 0;
}

.vpos-receipt-tbl th {
  border-bottom: 1px dashed #000;
  padding: 3px 0;
  font-size: 10.5px;
  text-align: left;
  font-weight: 700;
}

.vpos-receipt-tbl th.r, .vpos-receipt-tbl td.r {
  text-align: right;
}

.vpos-receipt-tbl td {
  padding: 3px 0;
  font-size: 11px;
  vertical-align: top;
}

.vpos-receipt-grand-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14.5px;
  font-weight: 900;
  color: #000;
  padding: 4px 0;
}

.vpos-receipt-foot-msg {
  text-align: center;
  font-size: 9.5px;
  color: #555;
  margin-top: 8px;
}

@media print {
  @page {
    size: 80mm auto;
    margin: 0;
  }
  html, body {
    margin: 0 !important;
    padding: 0 !important;
    background: #fff !important;
    color: #000 !important;
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
    width: 80mm !important;
    max-width: 80mm !important;
    padding: 4mm 3mm !important;
    margin: 0 !important;
    box-sizing: border-box !important;
    box-shadow: none !important;
    border: none !important;
    page-break-inside: avoid !important;
    page-break-after: avoid !important;
  }
}
"""

if '/* ── Aggressively Hide ERPNext Default Website Header' not in content:
    content = content.replace('</style>', css_to_add_or_replace + '\n</style>', 1)
    print('Added header/footer suppression & thermal receipt CSS.')

# 2. Replace _buildReceiptDom method
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
      <div class="vpos-receipt">
        <div class="vpos-receipt-co">${company}</div>
        <div class="vpos-receipt-sub">Vehicle Management System & Services</div>
        
        <div class="vpos-receipt-not-official">
          *** NOT AN OFFICIAL RECEIPT ***<br>
          <span style="font-size:9px;font-weight:600;">(ORDER SLIP / TRANSACTION RECORD)</span>
        </div>

        <div class="vpos-receipt-row"><span>Bill No:</span><b>${invoiceNo}</b></div>
        <div class="vpos-receipt-row"><span>Date & Time:</span><span>${date} ${time ? '· ' + time : ''}</span></div>
        <div class="vpos-receipt-row"><span>Cashier:</span><span>${cashier}</span></div>

        ${(customer || vehicle) ? `
          <div class="vpos-receipt-sep"></div>
          ${customer ? `<div class="vpos-receipt-row"><span>Customer:</span><b>${customer}</b></div>` : ''}
          ${vehicle ? `<div class="vpos-receipt-row"><span>Vehicle:</span><b>${vehicle}</b></div>` : ''}
        ` : ''}

        <div class="vpos-receipt-sep-solid"></div>
        <div style="font-weight:700;font-size:10.5px;margin-bottom:2px;">SOLD ITEMS</div>
        <div class="vpos-recitle-body">${itemsHtml || '<div style="color:#555;font-style:italic;">No items.</div>'}</div>

        ${discountAmount ? `
          <div class="vpos-receipt-sep"></div>
          <div class="vpos-receipt-row"><span>Discount</span><span>${discountAmount}</span></div>
        ` : ''}

        <div class="vpos-receipt-sep-solid"></div>
        <div class="vpos-receipt-grand-row">
          <span>TOTAL:</span>
          <span>${totalAmount}</span>
        </div>
        <div class="vpos-receipt-sep"></div>

        <div class="vpos-receipt-row"><span>Payment Method:</span><b>${paymentMethod}</b></div>
        ${paidAmount ? `<div class="vpos-receipt-row"><span>Amount Tendered:</span><span>${paidAmount}</span></div>` : ''}
        ${changeAmount ? `<div class="vpos-receipt-row"><span>Change Due:</span><b>${changeAmount}</b></div>` : ''}

        ${remarks ? `
          <div class="vpos-receipt-sep"></div>
          <div class="vpos-receipt-row"><span>Notes:</span><span>${remarks}</span></div>
        ` : ''}

        <div class="vpos-receipt-sep"></div>
        <div class="vpos-receipt-not-official" style="margin-top:6px;">
          *** THIS IS NOT AN OFFICIAL RECEIPT ***
        </div>
        <div class="vpos-receipt-foot-msg">
          Thank you for choosing ${company}!<br>
          Please keep this slip for your reference.
        </div>
      </div>`;

    const div = document.createElement("div");
    div.className = "vpos-receipt-box";
    div.innerHTML = html;
    return div;
  },"""

# Replace old _buildReceiptDom using regex
content = re.sub(r'  _buildReceiptDom\(sale\)\s*\{[\s\S]*?return div;\s*\},', new_build_receipt, content)
print('Updated _buildReceiptDom.')

# Save locally
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
print('Deployed to Web Page/vehicle-pos-terminal: HTTP', res.status)
