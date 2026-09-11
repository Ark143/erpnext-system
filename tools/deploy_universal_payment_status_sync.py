import json
import urllib.request
import urllib.parse
import http.cookiejar

BASE = "http://38.247.138.224:10017"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}

def login(usr="Administrator", pwd="admin"):
    login_h = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    with op.open(
        urllib.request.Request(
            BASE + "/api/method/login",
            data=f"usr={usr}&pwd={pwd}".encode(),
            headers=login_h,
            method="POST",
        ),
        timeout=30,
    ) as r:
        raw = r.read().decode()
        if "message" in raw and "Logged In" in raw:
            print("[OK] Logged into VPS as Administrator")

def call(path, method="GET", payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, headers=H, method=method)
    try:
        with op.open(req, timeout=120) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  HTTP {e.code} on {method} {path}: {body[:400]}")
        try:
            return json.loads(body)
        except Exception:
            return {"error": body}

login()

# Server Script code that computes precise outstanding amount and sets status: Paid, Partly Paid, Unpaid, or Overdue
universal_sync_code = """
def sync_single_voucher(voucher_type, voucher_no):
    if not voucher_no or voucher_type not in ("Sales Invoice", "Purchase Invoice"):
        return
        
    today = frappe.utils.nowdate()
    doc_fields = frappe.db.get_value(voucher_type, voucher_no, 
        ["grand_total", "rounded_total", "due_date", "docstatus", "custom_vehicle_job_order" if voucher_type == "Sales Invoice" else "name"],
        as_dict=True
    )
    if not doc_fields or doc_fields.docstatus != 1:
        return
        
    total = round(float(doc_fields.rounded_total or doc_fields.grand_total or 0.0), 2)
    due_date = str(doc_fields.due_date or today)
    
    # Sum from Payment Ledger Entry
    ple_res = frappe.db.sql('''
        SELECT coalesce(sum(amount), 0.0) as ple_balance
        FROM `tabPayment Ledger Entry`
        WHERE against_voucher_no = %s AND delinked = 0 AND docstatus = 1
    ''', (voucher_no,), as_dict=True)
    
    # For Sales Invoice: receivable amount is positive in PLE, payments are negative
    # For Purchase Invoice: payable amount is negative in PLE, payments are positive
    if voucher_type == "Sales Invoice":
        balance = round(float(ple_res[0].ple_balance if ple_res else 0.0), 2)
    else:
        balance = round(abs(float(ple_res[0].ple_balance if ple_res else 0.0)), 2)
        
    # If no PLE records exist at all, fall back to grand_total
    ple_count = frappe.db.sql('''
        SELECT count(*) as cnt FROM `tabPayment Ledger Entry` WHERE against_voucher_no = %s AND docstatus = 1
    ''', (voucher_no,), as_dict=True)[0].cnt
    
    if ple_count == 0:
        balance = total
        
    if balance < 0.01:
        outstanding = 0.0
        paid = total
        status = "Paid"
    elif balance < (total - 0.01):
        outstanding = balance
        paid = round(total - balance, 2)
        status = "Partly Paid"
    else:
        outstanding = total
        paid = 0.0
        if due_date < today:
            status = "Overdue"
        else:
            status = "Unpaid"
            
    frappe.db.set_value(voucher_type, voucher_no, {
        "outstanding_amount": outstanding,
        "paid_amount": paid,
        "status": status
    }, update_modified=False)
    
    # Sync Job Order
    if voucher_type == "Sales Invoice":
        jo = doc_fields.get("custom_vehicle_job_order")
        if jo and frappe.db.exists("Vehicle Job Order", jo):
            jo_docstatus = frappe.db.get_value("Vehicle Job Order", jo, "docstatus")
            if status == "Paid":
                jo_status = "Completed" if jo_docstatus == 1 else "Invoiced"
            elif status == "Partly Paid":
                jo_status = "Partly Paid"
            else:
                jo_status = "Invoiced"
                
            frappe.db.set_value("Vehicle Job Order", jo, {
                "paid_amount": paid,
                "status": jo_status
            }, update_modified=False)

# Sync references in current document (for Payment Entry, Journal Entry, etc.)
for ref in (doc.get("references") or doc.get("accounts") or []):
    v_type = ref.get("reference_doctype") or ref.get("against_voucher_type")
    v_no = ref.get("reference_name") or ref.get("against_voucher")
    if v_type and v_no:
        sync_single_voucher(v_type, v_no)

if doc.doctype in ("Sales Invoice", "Purchase Invoice"):
    sync_single_voucher(doc.doctype, doc.name)
"""

# Deploy DocType events on Payment Entry, Journal Entry, Sales Invoice, and Purchase Invoice
hook_configs = [
    ("Payment Entry", "After Submit", "VM Sync Payment Entry After Submit"),
    ("Payment Entry", "After Cancel", "VM Sync Payment Entry After Cancel"),
    ("Payment Entry", "After Save", "VM Sync Payment Entry After Save"),
    ("Journal Entry", "After Submit", "VM Sync Journal Entry After Submit"),
    ("Journal Entry", "After Cancel", "VM Sync Journal Entry After Cancel"),
    ("Sales Invoice", "After Submit", "VM Sync Sales Invoice After Submit"),
    ("Purchase Invoice", "After Submit", "VM Sync Purchase Invoice After Submit"),
]

for dt, event, script_name in hook_configs:
    payload = {
        "name": script_name,
        "doctype": "Server Script",
        "script_type": "DocType Event",
        "reference_doctype": dt,
        "doctype_event": event,
        "disabled": 0,
        "script": universal_sync_code
    }
    chk = call(f"/api/resource/Server%20Script/{urllib.parse.quote(script_name)}", "GET")
    if chk.get("data"):
        call(f"/api/resource/Server%20Script/{urllib.parse.quote(script_name)}", "PUT", {"script": universal_sync_code, "disabled": 0})
        print(f"  [OK] Updated Server Script: {script_name}")
    else:
        call("/api/resource/Server%20Script", "POST", payload)
        print(f"  [OK] Created Server Script: {script_name}")

# Now run a full database sweep on all submitted Sales Invoices and Purchase Invoices
full_sweep_script = """
today = frappe.utils.nowdate()

sinv_list = frappe.db.sql('''
    SELECT name, grand_total, rounded_total, due_date, status, outstanding_amount, paid_amount, custom_vehicle_job_order
    FROM `tabSales Invoice`
    WHERE docstatus = 1
''', as_dict=True)

stats = {"Paid": 0, "Partly Paid": 0, "Unpaid": 0, "Overdue": 0}
updated = []

for inv in sinv_list:
    v_no = inv.name
    total = round(float(inv.rounded_total or inv.grand_total or 0.0), 2)
    due_date = str(inv.due_date or today)
    
    ple_res = frappe.db.sql('''
        SELECT coalesce(sum(amount), 0.0) as ple_balance
        FROM `tabPayment Ledger Entry`
        WHERE against_voucher_no = %s AND delinked = 0 AND docstatus = 1
    ''', (v_no,), as_dict=True)
    
    ple_cnt = frappe.db.sql('''
        SELECT count(*) as cnt FROM `tabPayment Ledger Entry` WHERE against_voucher_no = %s AND docstatus = 1
    ''', (v_no,), as_dict=True)[0].cnt
    
    if ple_cnt == 0:
        balance = total
    else:
        balance = round(float(ple_res[0].ple_balance if ple_res else 0.0), 2)
        
    if balance < 0.01:
        outstanding = 0.0
        paid = total
        status = "Paid"
    elif balance < (total - 0.01):
        outstanding = balance
        paid = round(total - balance, 2)
        status = "Partly Paid"
    else:
        outstanding = total
        paid = 0.0
        if due_date < today:
            status = "Overdue"
        else:
            status = "Unpaid"
            
    stats[status] = stats.get(status, 0) + 1
    
    old_status = inv.status
    old_outstanding = round(float(inv.outstanding_amount or 0.0), 2)
    
    if old_status != status or abs(old_outstanding - outstanding) > 0.001:
        frappe.db.set_value("Sales Invoice", v_no, {
            "outstanding_amount": outstanding,
            "paid_amount": paid,
            "status": status
        }, update_modified=False)
        
        updated.append({
            "name": v_no,
            "old_status": old_status,
            "new_status": status,
            "grand_total": total,
            "paid": paid,
            "outstanding": outstanding
        })
        
        jo = inv.custom_vehicle_job_order
        if jo and frappe.db.exists("Vehicle Job Order", jo):
            jo_docstatus = frappe.db.get_value("Vehicle Job Order", jo, "docstatus")
            if status == "Paid":
                jo_status = "Completed" if jo_docstatus == 1 else "Invoiced"
            elif status == "Partly Paid":
                jo_status = "Partly Paid"
            else:
                jo_status = "Invoiced"
                
            frappe.db.set_value("Vehicle Job Order", jo, {
                "paid_amount": paid,
                "status": jo_status
            }, update_modified=False)

# Purchase Invoices
pinv_list = frappe.db.sql('''
    SELECT name, grand_total, rounded_total, due_date, status, outstanding_amount, paid_amount
    FROM `tabPurchase Invoice`
    WHERE docstatus = 1
''', as_dict=True)

p_stats = {"Paid": 0, "Partly Paid": 0, "Unpaid": 0, "Overdue": 0}

for pinv in pinv_list:
    v_no = pinv.name
    total = round(float(pinv.rounded_total or pinv.grand_total or 0.0), 2)
    due_date = str(pinv.due_date or today)
    
    ple_res = frappe.db.sql('''
        SELECT coalesce(sum(amount), 0.0) as ple_balance
        FROM `tabPayment Ledger Entry`
        WHERE against_voucher_no = %s AND delinked = 0 AND docstatus = 1
    ''', (v_no,), as_dict=True)
    
    ple_cnt = frappe.db.sql('''
        SELECT count(*) as cnt FROM `tabPayment Ledger Entry` WHERE against_voucher_no = %s AND docstatus = 1
    ''', (v_no,), as_dict=True)[0].cnt
    
    if ple_cnt == 0:
        balance = total
    else:
        balance = round(abs(float(ple_res[0].ple_balance if ple_res else 0.0)), 2)
        
    if balance < 0.01:
        outstanding = 0.0
        paid = total
        status = "Paid"
    elif balance < (total - 0.01):
        outstanding = balance
        paid = round(total - balance, 2)
        status = "Partly Paid"
    else:
        outstanding = total
        paid = 0.0
        if due_date < today:
            status = "Overdue"
        else:
            status = "Unpaid"
            
    p_stats[status] = p_stats.get(status, 0) + 1
    
    old_status = pinv.status
    old_outstanding = round(float(pinv.outstanding_amount or 0.0), 2)
    
    if old_status != status or abs(old_outstanding - outstanding) > 0.001:
        frappe.db.set_value("Purchase Invoice", v_no, {
            "outstanding_amount": outstanding,
            "paid_amount": paid,
            "status": status
        }, update_modified=False)

frappe.response["message"] = {
    "sales_invoice_stats": stats,
    "purchase_invoice_stats": p_stats,
    "updated_count": len(updated),
    "sample_updated": updated[:10]
}
"""

ss_sweep = {
    'name': 'VM Run Universal Invoice Sweep',
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_run_universal_invoice_sweep',
    'allow_guest': 0,
    'disabled': 0,
    'script': full_sweep_script
}

chk_sw = call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Run Universal Invoice Sweep')}", "GET")
if chk_sw.get("data"):
    call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Run Universal Invoice Sweep')}", "PUT", {"script": full_sweep_script, "disabled": 0})
else:
    call("/api/resource/Server%20Script", "POST", ss_sweep)

print("\n[Running Universal Database Sweep for Paid, Partly Paid, Unpaid, Overdue...]")
res_sw = call("/api/method/vm_run_universal_invoice_sweep", "POST", {})
rep_sw = res_sw.get("message", {})

print("\n================ SYSTEM INVOICE STATUS SUMMARY ================")
print("Sales Invoices Distribution:")
for k, v in rep_sw.get("sales_invoice_stats", {}).items():
    print(f"  • {k}: {v} invoices")

print("\nPurchase Invoices Distribution:")
for k, v in rep_sw.get("purchase_invoice_stats", {}).items():
    print(f"  • {k}: {v} invoices")

print(f"\nInvoices Updated during this sweep: {rep_sw.get('updated_count')}")
for u in rep_sw.get("sample_updated", []):
    print(f"  -> {u['name']}: {u['old_status']} -> {u['new_status']} (Total: {u['grand_total']}, Paid: {u['paid']}, Outstanding: {u['outstanding']})")
