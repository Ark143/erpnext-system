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

# Bank Reconciliation Script
recon_flow_script = """
# 1. Ensure Bank exists
bank_name = "BDO Unibank, Inc."
if not frappe.db.exists("Bank", bank_name):
    b = frappe.get_doc({
        "doctype": "Bank",
        "bank_name": bank_name,
        "swift_number": "BNORPHMM"
    })
    b.insert(ignore_permissions=True)

# 2. Ensure Bank Account exists
bank_account_title = "Automan Operating Account"
expected_ba_name = bank_account_title + " - " + bank_name
if frappe.db.exists("Bank Account", expected_ba_name):
    ba_name = expected_ba_name
else:
    ba = frappe.get_doc({
        "doctype": "Bank Account",
        "account_name": bank_account_title,
        "bank": bank_name,
        "account": "BDO - AUTOMAN",
        "company": "Automan Car Care Center",
        "is_company_account": 1,
        "is_default": 1,
        "bank_account_no": "0045-8921-3310"
    })
    ba.insert(ignore_permissions=True)
    ba_name = ba.name

# 3. Create a Bank Payment Entry (Customer deposit into BDO - AUTOMAN)
sample_cust = frappe.db.get_value("Customer", {"company": "Automan Car Care Center"}, "name") or "IRMOHEL SORIANO"

pe = frappe.get_doc({
    "doctype": "Payment Entry",
    "payment_type": "Receive",
    "payment_order_status": "Initiated",
    "posting_date": frappe.utils.nowdate(),
    "company": "Automan Car Care Center",
    "party_type": "Customer",
    "party": sample_cust,
    "paid_from": "Debtors - AUTOMAN",
    "paid_to": "BDO - AUTOMAN",
    "paid_amount": 5000.0,
    "received_amount": 5000.0,
    "reference_no": "CHECK-BDO-98421",
    "reference_date": frappe.utils.nowdate(),
    "remarks": "Bank collection for automotive services"
})
pe.insert(ignore_permissions=True)
pe.submit()
pe_name = pe.name

# 4. Create Bank Transaction (Bank Statement record from BDO)
bt = frappe.get_doc({
    "doctype": "Bank Transaction",
    "bank_account": ba_name,
    "company": "Automan Car Care Center",
    "date": frappe.utils.nowdate(),
    "deposit": 5000.0,
    "withdrawal": 0.0,
    "currency": "PHP",
    "description": "ONLINE TRANSFER INWARD - CHECK-BDO-98421",
    "reference_number": "CHECK-BDO-98421",
    "transaction_id": "TXN-BDO-20260911-5501"
})

bt.insert(ignore_permissions=True)
bt.submit()
bt_name = bt.name

# 5. Reconcile Bank Transaction with Payment Entry
# In ERPNext, add_payment_entries automatically allocates and updates clearance_date on the Payment Entry
bt_doc = frappe.get_doc("Bank Transaction", bt_name)
bt_doc.add_payment_entries([{"payment_doctype": "Payment Entry", "payment_name": pe_name}])
bt_doc.flags.ignore_permissions = True
bt_doc.save()


# Refresh documents to verify final state
bt_final = frappe.get_doc("Bank Transaction", bt_name)
pe_final = frappe.get_doc("Payment Entry", pe_name)

frappe.response["message"] = {
    "bank": bank_name,
    "bank_account": ba_name,
    "payment_entry": {
        "name": pe_name,
        "amount": pe_final.paid_amount,
        "paid_to": pe_final.paid_to,
        "clearance_date": str(pe_final.clearance_date),
        "status": pe_final.status
    },

    "bank_transaction": {
        "name": bt_name,
        "date": str(bt_final.date),
        "deposit": bt_final.deposit,
        "allocated_amount": bt_final.allocated_amount,
        "unallocated_amount": bt_final.unallocated_amount,
        "status": bt_final.status,
        "reference_number": bt_final.reference_number
    }
}
"""

ss_recon = {
    "name": "VM Execute Bank Recon Transaction",
    "doctype": "Server Script",
    "script_type": "API",
    "api_method": "vm_execute_bank_recon_transaction",
    "allow_guest": 0,
    "disabled": 0,
    "script": recon_flow_script
}

chk = call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Execute Bank Recon Transaction')}", "GET")
if chk.get("data"):
    call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Execute Bank Recon Transaction')}", "PUT", {"script": recon_flow_script, "disabled": 0})
else:
    call("/api/resource/Server%20Script", "POST", ss_recon)

print("[Executing Actual Bank Reconciliation Transaction on VPS...]")
res = call("/api/method/vm_execute_bank_recon_transaction", "POST", {})
print("\nBank Recon Result:")
print(json.dumps(res, indent=2))
