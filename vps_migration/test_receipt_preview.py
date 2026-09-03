import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# 1. Fetch real invoice data
r = opener.open('http://38.247.138.224:10017/api/method/vm_pos_get_invoice_receipt?invoice_name=ACC-PSINV-2026-00031')
inv = json.loads(r.read().decode())['message']

peso = lambda v: f"₱ {float(v or 0):,.2f}"

items_html = ""
for it in inv['items']:
    amt = float(it['amount'] or (it['qty'] * it['rate']))
    items_html += f"""
    <div style="margin: 8px 0; padding: 6px 0; border-bottom: 1px dashed #e2e8f0;">
      <div style="display: flex; justify-content: space-between; font-weight: 700; font-size: 14px; color: #0f172a;">
        <span>{it['item_name']}</span>
        <span>{peso(amt)}</span>
      </div>
      <div style="display: flex; justify-content: space-between; font-size: 12px; color: #64748b; margin-top: 2px;">
        <span>{it['qty']} {it['uom'] or 'PC'} × {peso(it['rate'])}</span>
      </div>
    </div>
    """

sample_receipt_html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Receipt Test Preview</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #0c1a18;
      display: flex;
      justify-content: center;
      padding: 40px;
      margin: 0;
    }}
    .receipt-card {{
      background: #ffffff;
      color: #111827;
      border-radius: 18px;
      width: 100%;
      max-width: 480px;
      padding: 28px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }}
    .co-title {{
      font-size: 20px;
      font-weight: 900;
      text-align: center;
      text-transform: uppercase;
      color: #0f172a;
    }}
    .co-sub {{
      font-size: 12px;
      text-align: center;
      color: #475569;
      margin-top: 2px;
    }}
    .banner {{
      margin: 12px 0;
      padding: 8px 10px;
      border: 1.5px dashed #dc2626;
      background: #fef2f2;
      text-align: center;
      font-weight: 800;
      font-size: 13px;
      color: #b91c1c;
      border-radius: 6px;
    }}
    .row {{
      display: flex;
      justify-content: space-between;
      margin: 4px 0;
      font-size: 13.5px;
    }}
    .row span:first-child {{ color: #475569; }}
    .row b, .row span:last-child {{ color: #0f172a; font-weight: 700; }}
    .sep {{ border-top: 1px dashed #cbd5e1; margin: 10px 0; }}
    .sep-bold {{ border-top: 2px solid #0f172a; margin: 12px 0; }}
    .grand-row {{
      display: flex;
      justify-content: space-between;
      font-size: 20px;
      font-weight: 900;
      color: #0f172a;
      padding: 6px 0;
    }}
    .foot {{
      text-align: center;
      font-size: 11.5px;
      color: #64748b;
      margin-top: 12px;
      line-height: 1.4;
    }}
  </style>
</head>
<body>
  <div class="receipt-card">
    <div class="co-title">{inv['company']}</div>
    <div class="co-sub">Vehicle Management System & Services</div>
    
    <div class="banner">
      *** THIS IS NOT AN OFFICIAL RECEIPT ***<br>
      <span style="font-size:10.5px;font-weight:600;">(ORDER SLIP / INTERNAL REFERENCE ONLY)</span>
    </div>

    <div class="row"><span>Bill / Invoice No:</span><b>{inv['invoice_no']}</b></div>
    <div class="row"><span>Date & Time:</span><span>{inv['posting_date']} {inv['posting_time']}</span></div>
    <div class="row"><span>Cashier / Staff:</span><span>{inv['cashier']}</span></div>

    <div class="sep"></div>
    <div class="row"><span>Customer:</span><b>{inv['customer_name']}</b></div>
    <div class="row"><span>Vehicle / Plate:</span><b>{inv['plate_no'] or inv['vehicle']}</b></div>

    <div class="sep-bold"></div>
    <div style="font-weight:800;font-size:12.5px;color:#0f172a;margin-bottom:4px;">ITEMS SOLD / SERVICES</div>
    {items_html}

    <div class="sep-bold"></div>
    <div class="grand-row">
      <span>TOTAL AMOUNT:</span>
      <span>{peso(inv['total_amount'])}</span>
    </div>
    <div class="sep"></div>

    <div class="row"><span>Payment Method:</span><b>{inv['payment_method']}</b></div>
    <div class="row"><span>Amount Tendered:</span><span>{peso(inv['paid_amount'])}</span></div>
    <div class="row"><span>Change Due:</span><b style="font-size:15px;color:#10b981;">{peso(inv['change_amount'])}</b></div>

    <div class="sep"></div>
    <div class="banner" style="margin-top:8px;">
      *** THIS IS NOT AN OFFICIAL RECEIPT ***
    </div>
    <div class="foot">
      Thank you for choosing {inv['company']}!<br>
      Please keep this order slip for warranty & vehicle reference.
    </div>
  </div>
</body>
</html>
"""

test_out_path = r'c:\Users\josem\erpnext-system\vps_migration\test_receipt_output.html'
with open(test_out_path, 'w', encoding='utf-8') as f:
    f.write(sample_receipt_html)

print('Generated standalone receipt preview at', test_out_path)
print('Verified structure with real invoice:', inv['invoice_no'])
