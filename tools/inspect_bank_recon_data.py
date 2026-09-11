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

# 1. Bank Accounts
ba_fields = urllib.parse.quote(json.dumps(["name", "account_name", "bank", "account", "company", "is_default"]))
res_ba = call(f"/api/resource/Bank%20Account?fields={ba_fields}")
print("Bank Accounts:", res_ba.get("data"))

# 2. Bank GL Accounts
f_acc = urllib.parse.quote(json.dumps([["account_type", "=", "Bank"]]))
fields_acc = urllib.parse.quote(json.dumps(["name", "account_name", "company", "account_currency"]))
res_acc = call(f"/api/resource/Account?filters={f_acc}&fields={fields_acc}")
print("\nBank GL Accounts:", res_acc.get("data"))

# 3. Existing Bank Transactions
fields_bt = urllib.parse.quote(json.dumps(["name", "date", "status", "deposit", "withdrawal", "bank_account", "company", "unallocated_amount"]))
res_bt = call(f"/api/resource/Bank%20Transaction?fields={fields_bt}&limit_page_length=20")
print("\nBank Transactions:", res_bt.get("data"))

# 4. Check Payment Entries with Bank mode of payment or paid_to/from Bank account
f_pe = urllib.parse.quote(json.dumps([["docstatus", "=", 1]]))
fields_pe = urllib.parse.quote(json.dumps(["name", "posting_date", "paid_amount", "paid_to", "paid_from", "clearance_date", "mode_of_payment", "company"]))
res_pe = call(f"/api/resource/Payment%20Entry?filters={f_pe}&fields={fields_pe}&limit_page_length=10")
print("\nSample Submitted Payment Entries:", res_pe.get("data"))
