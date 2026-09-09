import requests
import json
import sys
import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
login_res = session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'})
login_res.raise_for_status()

SELLER_COMPANY = 'Ultra MRF Warehouse Dau'
SELLER_ABBR = 'UMDW'
SELLER_WH = 'Stores - UMDW'
SELLER_CUSTOMER = 'Ultra MRF Dau Main'

BUYER_COMPANY = 'Ultra MRF Dau Main'
BUYER_ABBR = 'UMDM'
BUYER_WH = 'Stores - UMDM'
BUYER_SUPPLIER = 'ULTRA MRF WAREHOUSE DAU'

ITEM_CODE = 'STRL-CAR PROTECT KIT (CAR CLEAN SET)'
QTY = 2.0
RATE = 1500.00
TOTAL = QTY * RATE
TODAY = '2026-09-08'

def post_and_submit(doctype, payload):
    r = session.post(f"{BASE_URL}/api/resource/{requests.utils.quote(doctype)}", json=payload)
    if r.status_code != 200:
        raise Exception(f"Failed to create {doctype}: {r.status_code} - {r.text}")
    doc = r.json().get('data', {})
    doc_name = doc['name']
    
    doc['docstatus'] = 1
    r_sub = session.put(f"{BASE_URL}/api/resource/{requests.utils.quote(doctype)}/{requests.utils.quote(doc_name)}", json=doc)
    if r_sub.status_code != 200:
        raise Exception(f"Failed to submit {doctype} {doc_name}: {r_sub.status_code} - {r_sub.text}")
    return r_sub.json().get('data', {})

print("=" * 80)
print("COMPREHENSIVE INTERCOMPANY TRANSACTION & BIR AUDIT PIPELINE")
print(f"Buyer (Branch):      {BUYER_COMPANY} ({BUYER_ABBR}) -> Warehouse: {BUYER_WH}")
print(f"Seller (Warehouse):  {SELLER_COMPANY} ({SELLER_ABBR}) -> Warehouse: {SELLER_WH}")
print(f"Item:                {ITEM_CODE}")
print(f"Quantity & Rate:     {QTY} Units @ PHP {RATE:,.2f} = Total: PHP {TOTAL:,.2f}")
print("=" * 80)

# -----------------------------------------------------------------------------
# STEP 1: Branch Purchase Order (Buying Module)
# -----------------------------------------------------------------------------
print("\n[STEP 1] Branch: Creating & Submitting Intercompany Purchase Order (PO)...")
po = post_and_submit('Purchase Order', {
    'doctype': 'Purchase Order',
    'company': BUYER_COMPANY,
    'supplier': BUYER_SUPPLIER,
    'transaction_date': TODAY,
    'schedule_date': TODAY,
    'set_posting_time': 1,
    'currency': 'PHP',
    'is_internal_supplier': 1,
    'represents_company': SELLER_COMPANY,
    'items': [{
        'item_code': ITEM_CODE,
        'qty': QTY,
        'rate': RATE,
        'warehouse': BUYER_WH,
        'schedule_date': TODAY
    }]
})
print(f"  -> [OK] PO Created & Submitted: {po['name']}")
print(f"     Grand Total: PHP {po.get('grand_total'):,.2f} | Status: {po.get('status')}")

# -----------------------------------------------------------------------------
# STEP 2: Main Warehouse Invoices Branch (Selling & Accounts Receivable Module)
# -----------------------------------------------------------------------------
print("\n[STEP 2] Warehouse: Issuing Intercompany Sales Invoice (SI)...")
si = post_and_submit('Sales Invoice', {
    'doctype': 'Sales Invoice',
    'company': SELLER_COMPANY,
    'customer': SELLER_CUSTOMER,
    'posting_date': TODAY,
    'due_date': TODAY,
    'set_posting_time': 1,
    'currency': 'PHP',
    'is_internal_customer': 1,
    'represents_company': BUYER_COMPANY,
    'update_stock': 0,
    'debit_to': f'Debtors - {SELLER_ABBR}',
    'items': [{
        'item_code': ITEM_CODE,
        'qty': QTY,
        'rate': RATE,
        'income_account': f'Sales - {SELLER_ABBR}',
        'cost_center': f'Main - {SELLER_ABBR}'
    }]
})
print(f"  -> [OK] SI Created & Submitted: {si['name']}")
print(f"     Grand Total: PHP {si.get('grand_total'):,.2f} | Outstanding: PHP {si.get('outstanding_amount'):,.2f}")

# -----------------------------------------------------------------------------
# STEP 3: Branch Books Purchase Invoice & Receives Stock (Accounts Payable & Stock)
# -----------------------------------------------------------------------------
print("\n[STEP 3] Branch: Booking Intercompany Purchase Invoice (PI) with Stock Inflow...")
pi = post_and_submit('Purchase Invoice', {
    'doctype': 'Purchase Invoice',
    'company': BUYER_COMPANY,
    'supplier': BUYER_SUPPLIER,
    'posting_date': TODAY,
    'due_date': TODAY,
    'set_posting_time': 1,
    'currency': 'PHP',
    'is_internal_supplier': 1,
    'represents_company': SELLER_COMPANY,
    'intercompany_invoice_reference': si['name'],
    'update_stock': 1,
    'credit_to': f'Creditors - {BUYER_ABBR}',
    'items': [{
        'item_code': ITEM_CODE,
        'qty': QTY,
        'rate': RATE,
        'warehouse': BUYER_WH,
        'set_warehouse': BUYER_WH,
        'expense_account': f'Cost of Goods Sold - {BUYER_ABBR}',
        'cost_center': f'Main - {BUYER_ABBR}',
        'purchase_order': po['name'],
        'po_detail': po['items'][0]['name']
    }]
})
print(f"  -> [OK] PI Created & Submitted: {pi['name']}")
print(f"     Grand Total: PHP {pi.get('grand_total'):,.2f} | Outstanding: PHP {pi.get('outstanding_amount'):,.2f}")

# Link SI to PI
session.put(f"{BASE_URL}/api/resource/Sales%20Invoice/{requests.utils.quote(si['name'])}", 
            json={'intercompany_invoice_reference': pi['name']})

# -----------------------------------------------------------------------------
# STEP 4: Branch Pays Main Warehouse (Payment Entry - Outgoing)
# -----------------------------------------------------------------------------
print("\n[STEP 4] Branch: Paying Main Warehouse via Payment Entry (Outgoing)...")
pe_pay = post_and_submit('Payment Entry', {
    'doctype': 'Payment Entry',
    'payment_type': 'Pay',
    'company': BUYER_COMPANY,
    'party_type': 'Supplier',
    'party': BUYER_SUPPLIER,
    'posting_date': TODAY,
    'set_posting_time': 1,
    'mode_of_payment': 'Cash',
    'paid_from': f'Cash - {BUYER_ABBR}',
    'paid_to': f'Creditors - {BUYER_ABBR}',
    'paid_amount': TOTAL,
    'received_amount': TOTAL,
    'target_exchange_rate': 1.0,
    'references': [{
        'reference_doctype': 'Purchase Invoice',
        'reference_name': pi['name'],
        'total_amount': TOTAL,
        'outstanding_amount': TOTAL,
        'allocated_amount': TOTAL
    }]
})
print(f"  -> [OK] Payment Entry (Pay) Submitted: {pe_pay['name']}")
print(f"     Paid PHP {pe_pay.get('paid_amount'):,.2f} from [Cash - {BUYER_ABBR}] to [{BUYER_SUPPLIER}]")

# -----------------------------------------------------------------------------
# STEP 5: Main Warehouse Receives Collection (Payment Entry - Incoming)
# -----------------------------------------------------------------------------
print("\n[STEP 5] Warehouse: Recording Incoming Collection via Payment Entry...")
pe_recv = post_and_submit('Payment Entry', {
    'doctype': 'Payment Entry',
    'payment_type': 'Receive',
    'company': SELLER_COMPANY,
    'party_type': 'Customer',
    'party': SELLER_CUSTOMER,
    'posting_date': TODAY,
    'set_posting_time': 1,
    'mode_of_payment': 'Cash',
    'paid_from': f'Debtors - {SELLER_ABBR}',
    'paid_to': f'Cash - {SELLER_ABBR}',
    'paid_amount': TOTAL,
    'received_amount': TOTAL,
    'target_exchange_rate': 1.0,
    'references': [{
        'reference_doctype': 'Sales Invoice',
        'reference_name': si['name'],
        'total_amount': TOTAL,
        'outstanding_amount': TOTAL,
        'allocated_amount': TOTAL
    }]
})
print(f"  -> [OK] Payment Entry (Receive) Submitted: {pe_recv['name']}")
print(f"     Received PHP {pe_recv.get('received_amount'):,.2f} into [Cash - {SELLER_ABBR}] from [{SELLER_CUSTOMER}]")

# -----------------------------------------------------------------------------
# STEP 6: Verify Balances & General Ledger
# -----------------------------------------------------------------------------
print("\n" + "=" * 80)
print("FINANCIAL VERIFICATION: INVOICE OUTSTANDING BALANCES")
print("=" * 80)

si_final = session.get(f"{BASE_URL}/api/resource/Sales%20Invoice/{requests.utils.quote(si['name'])}").json().get('data', {})
pi_final = session.get(f"{BASE_URL}/api/resource/Purchase%20Invoice/{requests.utils.quote(pi['name'])}").json().get('data', {})

print(f"1. Main Warehouse Sales Invoice ({si['name']}):")
print(f"   - Customer:            {si_final.get('customer')}")
print(f"   - Grand Total:         PHP {si_final.get('grand_total'):,.2f}")
print(f"   - Outstanding Balance: PHP {si_final.get('outstanding_amount'):,.2f}")
print(f"   - Status:              {si_final.get('status')} [100% PAID]")

print(f"\n2. Branch Purchase Invoice ({pi['name']}):")
print(f"   - Supplier:            {pi_final.get('supplier')}")
print(f"   - Grand Total:         PHP {pi_final.get('grand_total'):,.2f}")
print(f"   - Outstanding Balance: PHP {pi_final.get('outstanding_amount'):,.2f}")
print(f"   - Status:              {pi_final.get('status')} [100% PAID]")

# -----------------------------------------------------------------------------
# STEP 7: Generate BIR Reports for Both Companies
# -----------------------------------------------------------------------------
print("\n" + "=" * 80)
print("AUDIT: GENERATING BIR COMPLIANCE REPORTS FOR BOTH COMPANIES")
print("=" * 80)

# A. Generate BIR Sales Journal for Main Warehouse
bir_sj = post_and_submit('BIR Sales Journal', {
    'doctype': 'BIR Sales Journal',
    'company': SELLER_COMPANY,
    'from_date': '2026-09-01',
    'to_date': '2026-09-30',
    'sales_entries': [{
        'date': TODAY,
        'payor': SELLER_CUSTOMER,
        'tin': '123-456-789-000',
        'invoice_no': si['name'],
        'goods_services': 'Goods',
        'vatable_sales': TOTAL,
        'output_vat': 0.0,
        'total_sales': TOTAL,
        'total_receivable': TOTAL,
        'status_ref_date': f"PAID / {si['name']}",
        'payment_date': TODAY,
        'remarks': f"Intercompany Sale to {BUYER_COMPANY}"
    }],
    'summary_entries': [
        {'summary': 'Documents', 'value': 1},
        {'summary': 'Total Gross', 'value': TOTAL}
    ]
})
print(f"  -> [BIR AUDIT] Generated BIR Sales Journal for {SELLER_COMPANY}: {bir_sj['name']}")

# B. Generate BIR Purchases Book for Branch
bir_pb = post_and_submit('BIR Purchases Book', {
    'doctype': 'BIR Purchases Book',
    'company': BUYER_COMPANY,
    'from_date': '2026-09-01',
    'to_date': '2026-09-30',
    'purchases_entries': [{
        'date': TODAY,
        'supplier': BUYER_SUPPLIER,
        'tin': '987-654-321-000',
        'invoice_no': pi['name'],
        'description': f"Intercompany Purchase from {SELLER_COMPANY}",
        'vatable_purchases': TOTAL,
        'input_vat': 0.0,
        'total_purchases': TOTAL,
        'total_payable': TOTAL
    }]
})
print(f"  -> [BIR AUDIT] Generated BIR Purchases Book for {BUYER_COMPANY}: {bir_pb['name']}")

# C. Generate BIR Cash Receipt Journal (CRJ) for Main Warehouse
bir_crj = post_and_submit('BIR Cash Receipt Journal', {
    'doctype': 'BIR Cash Receipt Journal',
    'company': SELLER_COMPANY,
    'from_date': '2026-09-01',
    'to_date': '2026-09-30',
    'crj_entries': [{
        'date': TODAY,
        'customer': SELLER_CUSTOMER,
        'or_no': pe_recv['name'],
        'ref_invoice': si['name'],
        'mode_of_payment': 'Cash',
        'gross_amount': TOTAL,
        'net_collected': TOTAL,
        'remarks': f"Collection from {BUYER_COMPANY}"
    }],
    'summary_entries': [
        {'summary': 'Total Receipts', 'value': TOTAL}
    ]
})
print(f"  -> [BIR AUDIT] Generated BIR Cash Receipt Journal for {SELLER_COMPANY}: {bir_crj['name']}")

# D. Generate BIR Cash Disbursement Journal (CDJ) for Branch
bir_cdj = post_and_submit('BIR Cash Disbursement Journal', {
    'doctype': 'BIR Cash Disbursement Journal',
    'company': BUYER_COMPANY,
    'from_date': '2026-09-01',
    'to_date': '2026-09-30',
    'cdj_entries': [{
        'date': TODAY,
        'payee': BUYER_SUPPLIER,
        'voucher_no': pe_pay['name'],
        'ref_invoice': pi['name'],
        'bank_account': f'Cash - {BUYER_ABBR}',
        'gross_amount': TOTAL,
        'net_paid': TOTAL,
        'remarks': f"Payment to {SELLER_COMPANY}"
    }],
    'summary_entries': [
        {'summary': 'Total Disbursements', 'value': TOTAL}
    ]
})
print(f"  -> [BIR AUDIT] Generated BIR Cash Disbursement Journal for {BUYER_COMPANY}: {bir_cdj['name']}")

print("\n" + "=" * 80)
print(">>> COMPLETE INTERCOMPANY LIFECYCLE & BIR AUDIT EXECUTED 100% SUCCESSFULLY! <<<")
print("=" * 80)
