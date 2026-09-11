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

# Inspect Sales Invoice ACC-SINV-2026-00449
res_inv = call("/api/resource/Sales%20Invoice/ACC-SINV-2026-00449", "GET")
inv = res_inv.get("data", {})

print("--- Sales Invoice ACC-SINV-2026-00449 ---")
fields_to_print = [
    "name", "docstatus", "status", "customer", "company", "posting_date",
    "grand_total", "rounded_total", "outstanding_amount", "paid_amount", "change_amount",
    "is_pos", "is_return", "custom_vehicle_job_order", "custom_vehicle_plate"
]
for f in fields_to_print:
    print(f"  {f}: {inv.get(f)}")

print("\nPayments child table:")
payments = inv.get("payments", [])
for p in payments:
    print(f"  Mode of Payment: {p.get('mode_of_payment')}, Amount: {p.get('amount')}, Base Amount: {p.get('base_amount')}")

# Check Payment Entry Reference
print("\nPayment Entry References:")
pe_refs = call('/api/resource/Payment%20Entry%20Reference?filters=[["reference_name","=","ACC-SINV-2026-00449"]]&fields=["parent","allocated_amount","outstanding_amount","docstatus"]', "GET")
for pr in pe_refs.get("data", []):
    print("  PE Ref:", pr)

# Check GL Entries for this invoice
print("\nGL Entries for ACC-SINV-2026-00449:")
gle = call('/api/resource/GL%20Entry?filters=[["voucher_no","=","ACC-SINV-2026-00449"]]&fields=["name","account","debit","credit","is_cancelled"]', "GET")
for g in gle.get("data", []):
    print("  GLE:", g)

# Check Payment Ledger Entry for this invoice
print("\nPayment Ledger Entries for ACC-SINV-2026-00449:")
ple = call('/api/resource/Payment%20Ledger%20Entry?filters=[["voucher_no","=","ACC-SINV-2026-00449"]]&fields=["name","amount","amount_in_account_currency","delinked"]', "GET")
for pl in ple.get("data", []):
    print("  PLE:", pl)

# Check Job Order JO-2026-00480 if referenced
if inv.get("custom_vehicle_job_order"):
    jo_name = inv.get("custom_vehicle_job_order")
    res_jo = call(f"/api/resource/Vehicle%20Job%20Order/{urllib.parse.quote(jo_name)}", "GET")
    jo = res_jo.get("data", {})
    print(f"\n--- Vehicle Job Order {jo_name} ---")
    for f in ["name", "status", "customer", "grand_total", "invoiced_amount", "paid_amount"]:
        if f in jo:
            print(f"  {f}: {jo.get(f)}")
