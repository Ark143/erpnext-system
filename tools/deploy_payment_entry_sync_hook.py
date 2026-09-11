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
        with op.open(req, timeout=60) as r:
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

# DocType Event for Payment Entry: on_submit
pe_sync_script = """
for ref in (doc.get("references") or []):
    inv_type = ref.get("reference_doctype")
    inv_name = ref.get("reference_name")
    if inv_type in ("Sales Invoice", "Purchase Invoice") and inv_name:
        ple_sum = frappe.db.sql('''
            SELECT coalesce(sum(amount), 0.0) as outstanding
            FROM `tabPayment Ledger Entry`
            WHERE against_voucher_no = %s AND delinked = 0 AND docstatus = 1
        ''', (inv_name,), as_dict=True)
        
        real_outstanding = round(abs(float(ple_sum[0].outstanding if ple_sum else 0.0)), 2)
        grand_total = round(float(frappe.db.get_value(inv_type, inv_name, "grand_total") or 0.0), 2)
        paid_amt = round(max(0.0, grand_total - real_outstanding), 2)
        
        if real_outstanding <= 0.001:
            new_status = "Paid"
            real_outstanding = 0.0
            paid_amt = grand_total
        elif real_outstanding < grand_total:
            new_status = "Partly Paid"
        else:
            new_status = "Unpaid"
            
        frappe.db.set_value(inv_type, inv_name, {
            "outstanding_amount": real_outstanding,
            "paid_amount": paid_amt,
            "status": new_status
        }, update_modified=False)
        
        if inv_type == "Sales Invoice":
            jo = frappe.db.get_value("Sales Invoice", inv_name, "custom_vehicle_job_order")
            if jo and frappe.db.exists("Vehicle Job Order", jo):
                jo_docstatus = frappe.db.get_value("Vehicle Job Order", jo, "docstatus")
                frappe.db.set_value("Vehicle Job Order", jo, {
                    "paid_amount": paid_amt,
                    "status": "Completed" if (new_status == "Paid" and jo_docstatus == 1) else "Invoiced"
                }, update_modified=False)
"""

for event in ["After Submit", "After Cancel"]:
    script_name = f"VM Auto Sync Invoice on Payment Entry {event}"
    payload = {
        "name": script_name,
        "doctype": "Server Script",
        "script_type": "DocType Event",
        "reference_doctype": "Payment Entry",
        "doctype_event": event,
        "disabled": 0,
        "script": pe_sync_script
    }
    chk = call(f"/api/resource/Server%20Script/{urllib.parse.quote(script_name)}", "GET")
    if chk.get("data"):
        call(f"/api/resource/Server%20Script/{urllib.parse.quote(script_name)}", "PUT", {"script": pe_sync_script, "disabled": 0})
        print(f"[OK] Updated Server Script: {script_name}")
    else:
        call("/api/resource/Server%20Script", "POST", payload)
        print(f"[OK] Created Server Script: {script_name}")

# Verify target invoice ACC-SINV-2026-00449
res_target = call("/api/resource/Sales%20Invoice/ACC-SINV-2026-00449", "GET")
t_inv = res_target.get("data", {})
print("\n================ VERIFICATION ================")
print(f"Sales Invoice:        {t_inv.get('name')}")
print(f"Customer:             {t_inv.get('customer')}")
print(f"Grand Total:          PHP {t_inv.get('grand_total'):,.2f}")
print(f"Paid Amount:          PHP {t_inv.get('paid_amount'):,.2f}")
print(f"Outstanding Amount:   PHP {t_inv.get('outstanding_amount'):,.2f}")
print(f"Status:               {t_inv.get('status')}")
