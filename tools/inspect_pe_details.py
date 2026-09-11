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

# Query Payment Entry References via server script / sql to get full picture
inspect_script = """
inv_name = 'ACC-SINV-2026-00449'

pe_refs = frappe.db.sql('''
    SELECT * FROM `tabPayment Entry Reference` WHERE reference_name = %s
''', (inv_name,), as_dict=True)

pe_docs = []
for pr in pe_refs:
    pe = frappe.db.sql('''
        SELECT name, docstatus, status, party, paid_amount, received_amount, posting_date, paid_to, mode_of_payment, company
        FROM `tabPayment Entry` WHERE name = %s
    ''', (pr.parent,), as_dict=True)
    if pe:
        pe_docs.append(pe[0])

# Also check all payments for customer IRMOHEL SORIANO
all_customer_pes = frappe.db.sql('''
    SELECT name, docstatus, status, party, paid_amount, received_amount, posting_date, mode_of_payment, company
    FROM `tabPayment Entry` WHERE party = 'IRMOHEL SORIANO'
''', as_dict=True)

# Also check PLE records for this invoice and customer
ple_records = frappe.db.sql('''
    SELECT * FROM `tabPayment Ledger Entry` 
    WHERE voucher_no = %s OR against_voucher_no = %s OR party = 'IRMOHEL SORIANO'
''', (inv_name, inv_name), as_dict=True)

# Also check Sales Invoice doc in DB
inv_db = frappe.db.sql('''
    SELECT name, docstatus, status, outstanding_amount, paid_amount, grand_total, is_pos, custom_vehicle_job_order
    FROM `tabSales Invoice` WHERE name = %s
''', (inv_name,), as_dict=True)

frappe.response['message'] = {
    'inv_db': inv_db,
    'pe_refs': pe_refs,
    'pe_docs': pe_docs,
    'all_customer_pes': all_customer_pes,
    'ple_records': ple_records
}
"""

ss_inspect = {
    'name': 'VM Inspect Invoice Payment DB',
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_inspect_invoice_payment_db',
    'allow_guest': 0,
    'disabled': 0,
    'script': inspect_script
}

chk = call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Inspect Invoice Payment DB')}", "GET")
if chk.get("data"):
    call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Inspect Invoice Payment DB')}", "PUT", {"script": inspect_script, "disabled": 0})
else:
    call("/api/resource/Server%20Script", "POST", ss_inspect)

res = call("/api/method/vm_inspect_invoice_payment_db", "POST", {})
rep = res.get("message", {})

print("\n--- Sales Invoice in DB ---")
print(rep.get("inv_db"))

print("\n--- Payment Entry References linked to ACC-SINV-2026-00449 ---")
for pr in rep.get("pe_refs", []):
    print(" ", pr)

print("\n--- Linked Payment Entry Documents ---")
for pe in rep.get("pe_docs", []):
    print(" ", pe)

print("\n--- All Payment Entries for IRMOHEL SORIANO ---")
for cpe in rep.get("all_customer_pes", []):
    print(" ", cpe)

print("\n--- Payment Ledger Entries (PLE) ---")
for pl in rep.get("ple_records", []):
    print(" ", pl)
