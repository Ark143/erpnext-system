import requests
import json
import sys
import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
login_res = session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'})
login_res.raise_for_status()
print(f"[OK] Logged in to {BASE_URL} as Administrator")

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
TODAY = datetime.date.today().strftime('%Y-%m-%d')

print("\n" + "=" * 80)
print(f"STARTING FULL INTERCOMPANY CYCLE")
print(f"Buyer (Branch):    {BUYER_COMPANY} (Warehouse: {BUYER_WH})")
print(f"Seller (Warehouse): {SELLER_COMPANY} (Warehouse: {SELLER_WH})")
print(f"Item:               {ITEM_CODE} | Qty: {QTY} | Unit Rate: PHP {RATE:,.2f} | Total: PHP {QTY*RATE:,.2f}")
print("=" * 80)

def post_doc(doctype, doc_data):
    r = session.post(f"{BASE_URL}/api/resource/{requests.utils.quote(doctype)}", json=doc_data)
    if r.status_code != 200:
        raise Exception(f"Failed to create {doctype}: {r.status_code} - {r.text}")
    return r.json().get('data', {})

def submit_doc(doctype, doc_name):
    doc = session.get(f"{BASE_URL}/api/resource/{requests.utils.quote(doctype)}/{requests.utils.quote(doc_name)}").json().get('data', {})
    doc['docstatus'] = 1
    r = session.put(f"{BASE_URL}/api/resource/{requests.utils.quote(doctype)}/{requests.utils.quote(doc_name)}", json=doc)
    if r.status_code != 200:
        raise Exception(f"Failed to submit {doctype} {doc_name}: {r.status_code} - {r.text}")
    return r.json().get('data', {})

# -----------------------------------------------------------------------------
# STEP 1: Branch Creates & Submits Purchase Order (PO)
# -----------------------------------------------------------------------------
print("\n[STEP 1] Branch creating Purchase Order (PO)...")
po_payload = {
    'doctype': 'Purchase Order',
    'company': BUYER_COMPANY,
    'supplier': BUYER_SUPPLIER,
    'transaction_date': TODAY,
    'schedule_date': TODAY,
    'currency': 'PHP',
    'is_internal_supplier': 1,
    'represents_company': SELLER_COMPANY,
    'items': [
        {
            'item_code': ITEM_CODE,
            'qty': QTY,
            'rate': RATE,
            'warehouse': BUYER_WH,
            'schedule_date': TODAY
        }
    ]
}
po_doc = post_doc('Purchase Order', po_payload)
po_name = po_doc['name']
po_submitted = submit_doc('Purchase Order', po_name)
print(f"  -> [OK] Purchase Order Created & Submitted: {po_name} (Total: PHP {po_submitted.get('grand_total'):,.2f})")

# -----------------------------------------------------------------------------
# STEP 2: Main Warehouse Creates & Submits Intercompany Sales Order (SO)
# -----------------------------------------------------------------------------
print("\n[STEP 2] Main Warehouse creating Intercompany Sales Order (SO)...")
so_payload = {
    'doctype': 'Sales Order',
    'company': SELLER_COMPANY,
    'customer': SELLER_CUSTOMER,
    'transaction_date': TODAY,
    'delivery_date': TODAY,
    'currency': 'PHP',
    'is_internal_customer': 1,
    'represents_company': BUYER_COMPANY,
    'intercompany_order_reference': po_name,
    'items': [
        {
            'item_code': ITEM_CODE,
            'qty': QTY,
            'rate': RATE,
            'warehouse': SELLER_WH,
            'delivery_date': TODAY
        }
    ]
}
so_doc = post_doc('Sales Order', so_payload)
so_name = so_doc['name']
so_submitted = submit_doc('Sales Order', so_name)
print(f"  -> [OK] Sales Order Created & Submitted: {so_name} (Linked to PO: {po_name})")

# Link PO back to SO
session.put(f"{BASE_URL}/api/resource/Purchase%20Order/{requests.utils.quote(po_name)}", 
            json={'intercompany_order_reference': so_name})

# -----------------------------------------------------------------------------
# STEP 3: Main Warehouse Ships Goods via Delivery Note (DN)
# -----------------------------------------------------------------------------
print("\n[STEP 3] Main Warehouse dispatching stock via Delivery Note (DN)...")
so_item = so_submitted['items'][0]
dn_payload = {
    'doctype': 'Delivery Note',
    'company': SELLER_COMPANY,
    'customer': SELLER_CUSTOMER,
    'posting_date': TODAY,
    'currency': 'PHP',
    'is_internal_customer': 1,
    'represents_company': BUYER_COMPANY,
    'items': [
        {
            'item_code': ITEM_CODE,
            'qty': QTY,
            'rate': RATE,
            'warehouse': SELLER_WH,
            'against_sales_order': so_name,
            'so_detail': so_item['name']
        }
    ]
}
dn_doc = post_doc('Delivery Note', dn_payload)
dn_name = dn_doc['name']
dn_submitted = submit_doc('Delivery Note', dn_name)
print(f"  -> [OK] Delivery Note Created & Submitted: {dn_name} (Deducted {QTY} from {SELLER_WH})")

# -----------------------------------------------------------------------------
# STEP 4: Branch Receives Goods via Purchase Receipt (PR)
# -----------------------------------------------------------------------------
print("\n[STEP 4] Branch receiving stock via Purchase Receipt (PR)...")
po_item = po_submitted['items'][0]
pr_payload = {
    'doctype': 'Purchase Receipt',
    'company': BUYER_COMPANY,
    'supplier': BUYER_SUPPLIER,
    'posting_date': TODAY,
    'currency': 'PHP',
    'is_internal_supplier': 1,
    'represents_company': SELLER_COMPANY,
    'intercompany_reference': dn_name,
    'items': [
        {
            'item_code': ITEM_CODE,
            'qty': QTY,
            'rate': RATE,
            'warehouse': BUYER_WH,
            'purchase_order': po_name,
            'purchase_order_item': po_item['name']
        }
    ]
}
pr_doc = post_doc('Purchase Receipt', pr_payload)
pr_name = pr_doc['name']
pr_submitted = submit_doc('Purchase Receipt', pr_name)
print(f"  -> [OK] Purchase Receipt Created & Submitted: {pr_name} (Added {QTY} into {BUYER_WH})")

# -----------------------------------------------------------------------------
# STEP 5: Main Warehouse Invoices Branch via Sales Invoice (SI)
# -----------------------------------------------------------------------------
print("\n[STEP 5] Main Warehouse billing Branch via Sales Invoice (SI)...")
dn_item = dn_submitted['items'][0]
si_payload = {
    'doctype': 'Sales Invoice',
    'company': SELLER_COMPANY,
    'customer': SELLER_CUSTOMER,
    'posting_date': TODAY,
    'due_date': TODAY,
    'currency': 'PHP',
    'is_internal_customer': 1,
    'represents_company': BUYER_COMPANY,
    'update_stock': 0,
    'debit_to': f'Debtors - {SELLER_ABBR}',
    'items': [
        {
            'item_code': ITEM_CODE,
            'qty': QTY,
            'rate': RATE,
            'income_account': f'Sales - {SELLER_ABBR}',
            'cost_center': f'Main - {SELLER_ABBR}',
            'sales_order': so_name,
            'so_detail': so_item['name'],
            'delivery_note': dn_name,
            'dn_detail': dn_item['name']
        }
    ]
}
si_doc = post_doc('Sales Invoice', si_payload)
si_name = si_doc['name']
si_submitted = submit_doc('Sales Invoice', si_name)
print(f"  -> [OK] Sales Invoice Created & Submitted: {si_name} (AR Total: PHP {si_submitted.get('grand_total'):,.2f})")

# -----------------------------------------------------------------------------
# STEP 6: Branch Records Vendor Bill via Purchase Invoice (PI)
# -----------------------------------------------------------------------------
print("\n[STEP 6] Branch booking AP via Purchase Invoice (PI)...")
pr_item = pr_submitted['items'][0]
pi_payload = {
    'doctype': 'Purchase Invoice',
    'company': BUYER_COMPANY,
    'supplier': BUYER_SUPPLIER,
    'posting_date': TODAY,
    'due_date': TODAY,
    'currency': 'PHP',
    'is_internal_supplier': 1,
    'represents_company': SELLER_COMPANY,
    'intercompany_invoice_reference': si_name,
    'credit_to': f'Creditors - {BUYER_ABBR}',
    'items': [
        {
            'item_code': ITEM_CODE,
            'qty': QTY,
            'rate': RATE,
            'expense_account': f'Stock Received But Not Billed - {BUYER_ABBR}',
            'cost_center': f'Main - {BUYER_ABBR}',
            'purchase_order': po_name,
            'po_detail': po_item['name'],
            'purchase_receipt': pr_name,
            'pr_detail': pr_item['name']
        }
    ]
}
pi_doc = post_doc('Purchase Invoice', pi_payload)
pi_name = pi_doc['name']
pi_submitted = submit_doc('Purchase Invoice', pi_name)
print(f"  -> [OK] Purchase Invoice Created & Submitted: {pi_name} (AP Total: PHP {pi_submitted.get('grand_total'):,.2f})")

# Link SI to PI
session.put(f"{BASE_URL}/api/resource/Sales%20Invoice/{requests.utils.quote(si_name)}", 
            json={'intercompany_invoice_reference': pi_name})

# -----------------------------------------------------------------------------
# STEP 7: Branch Pays Main Warehouse via Payment Entry (Outgoing Pay)
# -----------------------------------------------------------------------------
print("\n[STEP 7] Branch executing Outgoing Payment to Main Warehouse...")
pe_pay_payload = {
    'doctype': 'Payment Entry',
    'payment_type': 'Pay',
    'company': BUYER_COMPANY,
    'party_type': 'Supplier',
    'party': BUYER_SUPPLIER,
    'posting_date': TODAY,
    'mode_of_payment': 'Cash',
    'paid_from': f'Cash - {BUYER_ABBR}',
    'paid_to': f'Creditors - {BUYER_ABBR}',
    'paid_amount': QTY * RATE,
    'received_amount': QTY * RATE,
    'target_exchange_rate': 1.0,
    'references': [
        {
            'reference_doctype': 'Purchase Invoice',
            'reference_name': pi_name,
            'total_amount': QTY * RATE,
            'outstanding_amount': QTY * RATE,
            'allocated_amount': QTY * RATE
        }
    ]
}
pe_pay_doc = post_doc('Payment Entry', pe_pay_payload)
pe_pay_name = pe_pay_doc['name']
pe_pay_submitted = submit_doc('Payment Entry', pe_pay_name)
print(f"  -> [OK] Branch Payment Entry Created & Submitted: {pe_pay_name} (Paid PHP {pe_pay_submitted.get('paid_amount'):,.2f})")

# -----------------------------------------------------------------------------
# STEP 8: Main Warehouse Records Collection via Payment Entry (Incoming Receive)
# -----------------------------------------------------------------------------
print("\n[STEP 8] Main Warehouse executing Incoming Payment Entry from Branch...")
pe_recv_payload = {
    'doctype': 'Payment Entry',
    'payment_type': 'Receive',
    'company': SELLER_COMPANY,
    'party_type': 'Customer',
    'party': SELLER_CUSTOMER,
    'posting_date': TODAY,
    'mode_of_payment': 'Cash',
    'paid_from': f'Debtors - {SELLER_ABBR}',
    'paid_to': f'Cash - {SELLER_ABBR}',
    'paid_amount': QTY * RATE,
    'received_amount': QTY * RATE,
    'target_exchange_rate': 1.0,
    'references': [
        {
            'reference_doctype': 'Sales Invoice',
            'reference_name': si_name,
            'total_amount': QTY * RATE,
            'outstanding_amount': QTY * RATE,
            'allocated_amount': QTY * RATE
        }
    ]
}
pe_recv_doc = post_doc('Payment Entry', pe_recv_payload)
pe_recv_name = pe_recv_doc['name']
pe_recv_submitted = submit_doc('Payment Entry', pe_recv_name)
print(f"  -> [OK] Main Warehouse Payment Entry Created & Submitted: {pe_recv_name} (Received PHP {pe_recv_submitted.get('received_amount'):,.2f})")

# -----------------------------------------------------------------------------
# STEP 9: Final Audit & Verifications
# -----------------------------------------------------------------------------
print("\n" + "=" * 80)
print("VERIFYING INVOICE OUTSTANDING BALANCES & GL/STOCK LEDGERS")
print("=" * 80)

# Verify Sales Invoice Outstanding
si_fresh = session.get(f"{BASE_URL}/api/resource/Sales%20Invoice/{requests.utils.quote(si_name)}").json().get('data', {})
print(f"Sales Invoice ({si_name}) Outstanding Amount: PHP {si_fresh.get('outstanding_amount'):,.2f} (Status: {si_fresh.get('status')})")

# Verify Purchase Invoice Outstanding
pi_fresh = session.get(f"{BASE_URL}/api/resource/Purchase%20Invoice/{requests.utils.quote(pi_name)}").json().get('data', {})
print(f"Purchase Invoice ({pi_name}) Outstanding Amount: PHP {pi_fresh.get('outstanding_amount'):,.2f} (Status: {pi_fresh.get('status')})")

# Check Stock Ledger for item
sle_res = session.get(f"{BASE_URL}/api/resource/Stock%20Ledger%20Entry?filters=[[\"item_code\",\"=\",\"{ITEM_CODE}\"]]&fields=[\"posting_date\",\"voucher_type\",\"voucher_no\",\"warehouse\",\"actual_qty\",\"qty_after_transaction\"]&order_by=creation%20desc&limit_page_length=5").json().get('data', [])
print("\nRecent Stock Ledger Entries for Item:")
for sle in sle_res:
    print(f"  {sle['voucher_type']} ({sle['voucher_no']}) -> {sle['warehouse']}: delta {sle['actual_qty']} => Balance {sle['qty_after_transaction']}")

print("\n" + "=" * 80)
print(">>> INTERCOMPANY TRANSACTION LIFECYCLE COMPLETED 100% SUCCESSFULLY! <<<")
print("=" * 80)
