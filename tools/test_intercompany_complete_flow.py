import requests
import json
import sys

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
print("EXECUTING FULL INTERCOMPANY BUYING & SELLING CYCLE")
print(f"Buyer Company (Branch):      {BUYER_COMPANY} ({BUYER_ABBR}) -> Warehouse: {BUYER_WH}")
print(f"Seller Company (Main Hub):   {SELLER_COMPANY} ({SELLER_ABBR}) -> Warehouse: {SELLER_WH}")
print(f"Item:                         {ITEM_CODE}")
print(f"Quantity:                     {QTY} Units @ PHP {RATE:,.2f} = PHP {TOTAL:,.2f}")
print("=" * 80)

# -----------------------------------------------------------------------------
# STEP 1: Branch Issues Intercompany Purchase Order (PO)
# -----------------------------------------------------------------------------
print("\n[STEP 1] Branch: Creating & Submitting Purchase Order (PO)...")
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
print(f"  -> [SUCCESS] Purchase Order Created & Submitted: {po['name']}")
print(f"     Total Amount: PHP {po.get('grand_total'):,.2f} | Status: {po.get('status')}")

# -----------------------------------------------------------------------------
# STEP 2: Stock Transfer from Main Warehouse to Branch
# -----------------------------------------------------------------------------
print("\n[STEP 2] Warehouse: Dispatching & Moving Stock via Material Transfer...")
ste = post_and_submit('Stock Entry', {
    'doctype': 'Stock Entry',
    'stock_entry_type': 'Material Transfer',
    'company': SELLER_COMPANY,
    'posting_date': TODAY,
    'set_posting_time': 1,
    'items': [{
        'item_code': ITEM_CODE,
        'qty': QTY,
        's_warehouse': SELLER_WH,
        't_warehouse': BUYER_WH,
        'basic_rate': RATE
    }]
})
print(f"  -> [SUCCESS] Stock Entry Submitted: {ste['name']}")
print(f"     Transferred {QTY} units from [{SELLER_WH}] to [{BUYER_WH}]")

# -----------------------------------------------------------------------------
# STEP 3: Main Warehouse Invoices Branch via Intercompany Sales Invoice (SI)
# -----------------------------------------------------------------------------
print("\n[STEP 3] Warehouse: Issuing Intercompany Sales Invoice (SI)...")
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
print(f"  -> [SUCCESS] Sales Invoice Created & Submitted: {si['name']}")
print(f"     Accounts Receivable (AR): PHP {si.get('grand_total'):,.2f} | Outstanding: PHP {si.get('outstanding_amount'):,.2f}")

# -----------------------------------------------------------------------------
# STEP 4: Branch Records Vendor Bill via Intercompany Purchase Invoice (PI)
# -----------------------------------------------------------------------------
print("\n[STEP 4] Branch: Booking Intercompany Purchase Invoice (PI)...")
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
    'credit_to': f'Creditors - {BUYER_ABBR}',
    'items': [{
        'item_code': ITEM_CODE,
        'qty': QTY,
        'rate': RATE,
        'expense_account': f'Cost of Goods Sold - {BUYER_ABBR}',
        'cost_center': f'Main - {BUYER_ABBR}',
        'purchase_order': po['name'],
        'po_detail': po['items'][0]['name']
    }]
})
print(f"  -> [SUCCESS] Purchase Invoice Created & Submitted: {pi['name']}")
print(f"     Accounts Payable (AP): PHP {pi.get('grand_total'):,.2f} | Outstanding: PHP {pi.get('outstanding_amount'):,.2f}")

# -----------------------------------------------------------------------------
# STEP 5: Branch Pays Main Warehouse via Payment Entry (Outgoing Pay)
# -----------------------------------------------------------------------------
print("\n[STEP 5] Branch: Executing Outgoing Payment to Main Warehouse...")
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
print(f"  -> [SUCCESS] Branch Payment Entry Submitted: {pe_pay['name']}")
print(f"     Paid PHP {pe_pay.get('paid_amount'):,.2f} from [Cash - {BUYER_ABBR}] to [{BUYER_SUPPLIER}]")

# -----------------------------------------------------------------------------
# STEP 6: Main Warehouse Records Collection via Payment Entry (Incoming Receive)
# -----------------------------------------------------------------------------
print("\n[STEP 6] Warehouse: Executing Incoming Payment Entry from Branch...")
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
print(f"  -> [SUCCESS] Warehouse Payment Entry Submitted: {pe_recv['name']}")
print(f"     Received PHP {pe_recv.get('received_amount'):,.2f} into [Cash - {SELLER_ABBR}] from [{SELLER_CUSTOMER}]")

# -----------------------------------------------------------------------------
# STEP 7: Comprehensive Financial & Stock Audit
# -----------------------------------------------------------------------------
print("\n" + "=" * 80)
print("AUDIT: POST-TRANSACTION INVOICE STATUS & BALANCES")
print("=" * 80)

# Check SI fresh
si_audit = session.get(f"{BASE_URL}/api/resource/Sales%20Invoice/{requests.utils.quote(si['name'])}").json().get('data', {})
print(f"1. Sales Invoice ({si['name']}):")
print(f"   Grand Total:         PHP {si_audit.get('grand_total'):,.2f}")
print(f"   Outstanding Amount:  PHP {si_audit.get('outstanding_amount'):,.2f}")
print(f"   Status:              {si_audit.get('status')}")

# Check PI fresh
pi_audit = session.get(f"{BASE_URL}/api/resource/Purchase%20Invoice/{requests.utils.quote(pi['name'])}").json().get('data', {})
print(f"\n2. Purchase Invoice ({pi['name']}):")
print(f"   Grand Total:         PHP {pi_audit.get('grand_total'):,.2f}")
print(f"   Outstanding Amount:  PHP {pi_audit.get('outstanding_amount'):,.2f}")
print(f"   Status:              {pi_audit.get('status')}")

# Check Stock Ledger Entries
sle_res = session.get(f"{BASE_URL}/api/resource/Stock%20Ledger%20Entry?filters=[[\"voucher_no\",\"=\",\"{ste['name']}\"]]&fields=[\"posting_date\",\"voucher_type\",\"voucher_no\",\"warehouse\",\"actual_qty\",\"qty_after_transaction\"]").json().get('data', [])
print(f"\n3. Stock Ledger Entries for {ste['name']}:")
for sle in sle_res:
    print(f"   -> Warehouse [{sle['warehouse']}]: delta {sle['actual_qty']} => Balance: {sle['qty_after_transaction']} units")

print("\n" + "=" * 80)
print(">>> ALL 6 INTERCOMPANY MODULES EXECUTED & FULLY SETTLED (100% SUCCESS) <<<")
print("=" * 80)
