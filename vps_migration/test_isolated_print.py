import urllib.request, urllib.parse, json

# Generate standalone HTML receipt for testing
def generate_receipt_html(sale):
    peso = lambda v: f"₱ {float(v or 0):,.2f}"
    company = sale.get('company') or 'ULTRA MRF'
    cashier = sale.get('cashier') or 'Cashier'
    date = sale.get('date') or ''
    time = sale.get('time') or ''
    invoice_no = sale.get('invoice_no') or 'POS-0000'
    vehicle = sale.get('vehicle_name') or sale.get('vehicle') or ''
    customer = sale.get('customer_name') or sale.get('customer') or 'Walk-in Customer'
    payment_method = sale.get('payment_method') or 'Cash'
    paid_amount = peso(sale.get('paid_amount') or 0)
    change_amount = peso(sale.get('change_amount') or 0)
    total_amount = peso(sale.get('total_amount') or 0)
    discount_amount = peso(sale.get('discount_amount') or 0) if float(sale.get('discount_amount') or 0) > 0 else ''
    remarks = sale.get('remarks') or ''
    items = sale.get('items') or []

    items_rows = ""
    for it in items:
        amt = float(it.get('amount') or (it.get('qty', 1) * it.get('rate', 0)))
        items_rows += f"""
        <tr>
          <td style="padding: 4px 0; vertical-align: top; font-weight: 700; width: 60%;">{it.get('item_name') or it.get('item_code')}<br>
            <span style="font-size: 11px; font-weight: 400; color: #555;">{it.get('qty')} {it.get('uom') or 'PC'} × {peso(it.get('rate'))}</span>
          </td>
          <td style="padding: 4px 0; vertical-align: top; text-align: right; font-weight: 700; width: 40%;">{peso(amt)}</td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Receipt - {invoice_no}</title>
<style>
  @page {{
    size: 80mm auto;
    margin: 0;
  }}
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Courier New', monospace;
    font-size: 12.5px;
    line-height: 1.4;
    color: #000000;
    background: #ffffff;
    width: 76mm;
    max-width: 76mm;
    margin: 0 auto;
    padding: 4mm 3mm;
  }}
  .center {{ text-align: center; }}
  .bold {{ font-weight: 700; }}
  .co-name {{ font-size: 17px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.5px; }}
  .co-sub {{ font-size: 11px; color: #333; margin-top: 1px; }}
  
  .not-official {{
    margin: 8px 0;
    padding: 6px 4px;
    border: 1.5px dashed #000;
    text-align: center;
    font-weight: 800;
    font-size: 11px;
    line-height: 1.3;
    background: #f9f9f9;
  }}
  
  .sep-dash {{ border-top: 1px dashed #777; margin: 6px 0; }}
  .sep-solid {{ border-top: 1.5px solid #000; margin: 8px 0; }}
  
  .row {{
    display: flex;
    justify-content: space-between;
    margin: 2px 0;
    font-size: 12px;
  }}
  .row .lbl {{ color: #444; }}
  .row .val {{ font-weight: 700; text-align: right; }}
  
  .tbl {{
    width: 100%;
    border-collapse: collapse;
    margin: 4px 0;
  }}
  .tbl th {{
    border-bottom: 1px dashed #000;
    padding: 4px 0;
    font-size: 11px;
    text-align: left;
    font-weight: 700;
  }}
  .tbl th.r {{ text-align: right; }}
  
  .grand-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 16px;
    font-weight: 900;
    padding: 4px 0;
  }}
  
  .footer-msg {{
    text-align: center;
    font-size: 10.5px;
    color: #444;
    margin-top: 8px;
    line-height: 1.3;
  }}
</style>
</head>
<body onload="window.print()">
  <div class="center co-name">{company}</div>
  <div class="center co-sub">Vehicle Management System &amp; Services</div>

  <div class="not-official">
    *** THIS IS NOT AN OFFICIAL RECEIPT ***<br>
    <span style="font-size: 9.5px; font-weight: 600;">(ORDER SLIP / TRANSACTION RECORD)</span>
  </div>

  <div class="row"><span class="lbl">Bill No:</span><span class="val">{invoice_no}</span></div>
  <div class="row"><span class="lbl">Date &amp; Time:</span><span class="val">{date} {time}</span></div>
  <div class="row"><span class="lbl">Cashier:</span><span class="val">{cashier}</span></div>

  <div class="sep-dash"></div>
  <div class="row"><span class="lbl">Customer:</span><span class="val">{customer}</span></div>
  {f'<div class="row"><span class="lbl">Vehicle:</span><span class="val">{vehicle}</span></div>' if vehicle else ''}

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
      {items_rows}
    </tbody>
  </table>

  {f'<div class="sep-dash"></div><div class="row"><span class="lbl">Discount:</span><span class="val">-{discount_amount}</span></div>' if discount_amount else ''}

  <div class="sep-solid"></div>
  <div class="grand-row">
    <span>TOTAL:</span>
    <span>{total_amount}</span>
  </div>
  <div class="sep-dash"></div>

  <div class="row"><span class="lbl">Payment Method:</span><span class="val">{payment_method}</span></div>
  <div class="row"><span class="lbl">Amount Tendered:</span><span class="val">{paid_amount}</span></div>
  <div class="row"><span class="lbl">Change Due:</span><span class="val" style="font-size: 13.5px;">{change_amount}</span></div>

  {f'<div class="sep-dash"></div><div class="row"><span class="lbl">Remarks:</span><span class="val">{remarks}</span></div>' if remarks else ''}

  <div class="sep-dash"></div>
  <div class="not-official" style="margin-top: 6px;">
    *** THIS IS NOT AN OFFICIAL RECEIPT ***
  </div>
  <div class="footer-msg">
    Thank you for choosing {company}!<br>
    Please keep this slip for your reference.
  </div>
</body>
</html>"""

# Test with sample sale
sale_sample = {
    'company': 'Ultra MRF Dau Annex',
    'cashier': 'test123',
    'date': 'Thursday, Sep 3, 2026',
    'time': '09:45 PM',
    'invoice_no': 'ACC-PSINV-2026-00031',
    'customer_name': 'NELSON L. CASTILLO',
    'vehicle_name': 'CAZ4232 — Toyota Fortuner',
    'payment_method': 'Cash',
    'paid_amount': 200.0,
    'change_amount': 75.0,
    'total_amount': 125.0,
    'discount_amount': 0.0,
    'remarks': 'Regular PMS Check',
    'items': [
        {'item_code': 'STRL-CAR PROTECT KIT', 'item_name': 'STRL-CAR PROTECT KIT (CAR CLEAN SET)', 'qty': 1, 'rate': 125.0, 'amount': 125.0, 'uom': 'PC'}
    ]
}

html = generate_receipt_html(sale_sample)
with open(r'c:\Users\josem\erpnext-system\vps_migration\isolated_receipt.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Generated clean isolated receipt at isolated_receipt.html')
