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

# Server Script to recalculate outstanding amounts from Payment Ledger Entry for all submitted Sales Invoices and Purchase Invoices
sync_script = """
# 1. Sync Sales Invoices
sinv_list = frappe.db.sql('''
    SELECT name, customer, debit_to, grand_total, outstanding_amount, status, custom_vehicle_job_order
    FROM `tabSales Invoice`
    WHERE docstatus = 1
''', as_dict=True)

updated_sinv = []

for inv in sinv_list:
    inv_name = inv.name
    # Calculate balance from PLE
    ple_sum = frappe.db.sql('''
        SELECT coalesce(sum(amount), 0.0) as outstanding
        FROM `tabPayment Ledger Entry`
        WHERE against_voucher_no = %s AND delinked = 0 AND docstatus = 1
    ''', (inv_name,), as_dict=True)
    
    real_outstanding = round(float(ple_sum[0].outstanding if ple_sum else 0.0), 2)
    grand_total = round(float(inv.grand_total or 0.0), 2)
    paid_amt = round(max(0.0, grand_total - real_outstanding), 2)
    
    # Determine correct status
    if real_outstanding <= 0.001:
        new_status = "Paid"
        real_outstanding = 0.0
        paid_amt = grand_total
    elif real_outstanding < grand_total:
        new_status = "Partly Paid"
    else:
        new_status = "Unpaid"
        
    old_outstanding = round(float(inv.outstanding_amount or 0.0), 2)
    old_status = inv.status
    
    if abs(old_outstanding - real_outstanding) > 0.001 or old_status != new_status:
        frappe.db.set_value("Sales Invoice", inv_name, {
            "outstanding_amount": real_outstanding,
            "paid_amount": paid_amt,
            "status": new_status
        }, update_modified=False)
        
        updated_sinv.append({
            "name": inv_name,
            "old_outstanding": old_outstanding,
            "new_outstanding": real_outstanding,
            "old_status": old_status,
            "new_status": new_status,
            "paid_amount": paid_amt,
            "job_order": inv.custom_vehicle_job_order
        })
        
        # Also update linked Vehicle Job Order if paid
        if inv.custom_vehicle_job_order and frappe.db.exists("Vehicle Job Order", inv.custom_vehicle_job_order):
            jo_docstatus = frappe.db.get_value("Vehicle Job Order", inv.custom_vehicle_job_order, "docstatus")
            if new_status == "Paid":
                frappe.db.set_value("Vehicle Job Order", inv.custom_vehicle_job_order, {
                    "paid_amount": paid_amt,
                    "status": "Completed" if jo_docstatus == 1 else "Invoiced"
                }, update_modified=False)
            elif new_status == "Partly Paid":
                frappe.db.set_value("Vehicle Job Order", inv.custom_vehicle_job_order, {
                    "paid_amount": paid_amt
                }, update_modified=False)

# 2. Sync Purchase Invoices
pinv_list = frappe.db.sql('''
    SELECT name, supplier, credit_to, grand_total, outstanding_amount, status
    FROM `tabPurchase Invoice`
    WHERE docstatus = 1
''', as_dict=True)

updated_pinv = []

for pinv in pinv_list:
    pinv_name = pinv.name
    ple_sum = frappe.db.sql('''
        SELECT coalesce(sum(amount), 0.0) as outstanding
        FROM `tabPayment Ledger Entry`
        WHERE against_voucher_no = %s AND delinked = 0 AND docstatus = 1
    ''', (pinv_name,), as_dict=True)
    
    real_outstanding = round(abs(float(ple_sum[0].outstanding if ple_sum else 0.0)), 2)
    grand_total = round(float(pinv.grand_total or 0.0), 2)
    paid_amt = round(max(0.0, grand_total - real_outstanding), 2)
    
    if real_outstanding <= 0.001:
        new_status = "Paid"
        real_outstanding = 0.0
        paid_amt = grand_total
    elif real_outstanding < grand_total:
        new_status = "Partly Paid"
    else:
        new_status = "Unpaid"
        
    old_outstanding = round(float(pinv.outstanding_amount or 0.0), 2)
    old_status = pinv.status
    
    if abs(old_outstanding - real_outstanding) > 0.001 or old_status != new_status:
        frappe.db.set_value("Purchase Invoice", pinv_name, {
            "outstanding_amount": real_outstanding,
            "paid_amount": paid_amt,
            "status": new_status
        }, update_modified=False)
        
        updated_pinv.append({
            "name": pinv_name,
            "old_outstanding": old_outstanding,
            "new_outstanding": real_outstanding,
            "old_status": old_status,
            "new_status": new_status
        })

frappe.response["message"] = {
    "total_sales_invoices_scanned": len(sinv_list),
    "updated_sales_invoices": updated_sinv,
    "total_purchase_invoices_scanned": len(pinv_list),
    "updated_purchase_invoices": updated_pinv
}
"""

ss_doc = {
    'name': 'VM Sync All Invoices Outstanding',
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_sync_all_invoices_outstanding',
    'allow_guest': 0,
    'disabled': 0,
    'script': sync_script
}

chk = call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Sync All Invoices Outstanding')}", "GET")
if chk.get("data"):
    call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Sync All Invoices Outstanding')}", "PUT", {"script": sync_script, "disabled": 0})
else:
    call("/api/resource/Server%20Script", "POST", ss_doc)

print("[Executing Sync of Outstanding Amounts and Statuses across all Invoices...]")
res_sync = call("/api/method/vm_sync_all_invoices_outstanding", "POST", {})
rep = res_sync.get("message", {})

print(f"\n--- SALES INVOICES (Scanned: {rep.get('total_sales_invoices_scanned')}) ---")
updated_sinvs = rep.get("updated_sales_invoices", [])
print(f"Updated: {len(updated_sinvs)} invoices")
for inv in updated_sinvs:
    print(f"  * {inv['name']}: {inv['old_status']} (Outstanding: {inv['old_outstanding']}) -> {inv['new_status']} (Outstanding: {inv['new_outstanding']}, Paid: {inv['paid_amount']})")

print(f"\n--- PURCHASE INVOICES (Scanned: {rep.get('total_purchase_invoices_scanned')}) ---")
updated_pinvs = rep.get("updated_purchase_invoices", [])
print(f"Updated: {len(updated_pinvs)} invoices")
for pinv in updated_pinvs:
    print(f"  * {pinv['name']}: {pinv['old_status']} -> {pinv['new_status']} (Outstanding: {pinv['new_outstanding']})")

# Verify ACC-SINV-2026-00449 specifically
res_target = call("/api/resource/Sales%20Invoice/ACC-SINV-2026-00449", "GET")
t_inv = res_target.get("data", {})
print("\n================ VERIFICATION ================")
print(f"Sales Invoice:        {t_inv.get('name')}")
print(f"Customer:             {t_inv.get('customer')}")
print(f"Grand Total:          ₱ {t_inv.get('grand_total'):,.2f}")
print(f"Paid Amount:          ₱ {t_inv.get('paid_amount'):,.2f}")
print(f"Outstanding Amount:   ₱ {t_inv.get('outstanding_amount'):,.2f}")
print(f"Status:               {t_inv.get('status')}")
