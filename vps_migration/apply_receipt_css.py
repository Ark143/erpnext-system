import re, json, urllib.request, urllib.parse

# 1. Read current HTML
html_path = r'c:\Users\josem\erpnext-system\vps_migration\current_pos_terminal.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 2. Add CSS rules before </style>
new_css = """
/* Receipt Modal Overlay & Print Styling */
.vpos-receipt-overlay {
  position: fixed;
  inset: 0;
  background: rgba(12, 26, 24, 0.75);
  backdrop-filter: blur(4px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}
.vpos-receipt-dialog {
  background: #ffffff;
  color: #0c1a18;
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}
.vpos-receipt-dialog-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: #f4f7f6;
  border-bottom: 1px solid #e2e8e6;
  font-family: var(--font-head);
  font-weight: 700;
  font-size: 14px;
  color: #13302b;
}
.vpos-receipt-dialog-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #5b6b68;
  line-height: 1;
  padding: 4px;
}
.vpos-receipt-dialog-body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
  background: #fff;
}
.vpos-receipt-dialog-foot {
  display: flex;
  gap: 10px;
  padding: 14px 20px;
  background: #f4f7f6;
  border-top: 1px solid #e2e8e6;
}
.vpos-receipt-btn-print {
  flex: 2;
  background: var(--mint);
  color: #04201a;
  border: none;
  border-radius: 10px;
  padding: 12px 16px;
  font-weight: 800;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: background 0.15s;
}
.vpos-receipt-btn-print:hover {
  background: var(--mint-d);
}
.vpos-receipt-btn-desk {
  background: #e2e8e6;
  color: #13302b;
  border: none;
  border-radius: 10px;
  padding: 12px 14px;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
}
.vpos-receipt-btn-desk:hover {
  background: #d0dad7;
}
.vpos-receipt-btn-close {
  flex: 1;
  background: #e2e8e6;
  color: #13302b;
  border: none;
  border-radius: 10px;
  padding: 12px 14px;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
}
.vpos-receipt-btn-close:hover {
  background: #d0dad7;
}
.vpos-hist-print-btn {
  background: rgba(22, 199, 132, 0.12);
  color: #0fa76d;
  border: 1px solid rgba(22, 199, 132, 0.3);
  border-radius: 6px;
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  transition: all 0.15s;
}
.vpos-hist-print-btn:hover {
  background: var(--mint);
  color: #04201a;
  border-color: var(--mint);
}
@media print {
  body * { visibility: hidden !important; }
  .vpos-receipt-printable, .vpos-receipt-printable * { visibility: visible !important; }
  .vpos-receipt-printable {
    position: fixed !important;
    left: 0 !important;
    top: 0 !important;
    width: 100% !important;
    min-height: 100vh !important;
    margin: 0 !important;
    padding: 8mm 6mm !important;
    background: #fff !important;
    color: #000 !important;
    box-shadow: none !important;
    border: none !important;
    z-index: 999999 !important;
  }
}
"""

if '.vpos-receipt-overlay' not in content:
    content = content.replace('</style>', new_css + '\n</style>', 1)
    print('Added receipt CSS.')

# 3. Write updated JS methods for search, loadStock, totals, printReceipt, showReceiptModal, showReceiptForInvoice, renderHistoryList, submit
# Let's inspect where POS object methods are defined
print('POS object replacement...')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated current_pos_terminal.html with styles.')
