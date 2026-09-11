import json
import urllib.request
import urllib.parse
import http.cookiejar
import io
import mimetypes

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

# Generate sample Bank Statement CSV
csv_content = """Date,Deposit,Withdrawal,Description,Reference Number,Bank Account,Currency
2026-09-02,12500.00,,CUSTOMER ONLINE TRANSFER REF 9901,BDO-REF-9901,Automan Operating Account - BDO Unibank, Inc.,PHP
2026-09-04,,3500.00,SUPPLIER AUTO DEBIT PARTS,BDO-REF-9902,Automan Operating Account - BDO Unibank, Inc.,PHP
2026-09-07,8200.00,,CHECK DEPOSIT CLEARING 4410,BDO-REF-9903,Automan Operating Account - BDO Unibank, Inc.,PHP
2026-09-09,,1200.00,BANK SERVICE CHARGE,BDO-REF-9904,Automan Operating Account - BDO Unibank, Inc.,PHP
2026-09-10,25000.00,,FLEET SERVICE SETTLEMENT,BDO-REF-9905,Automan Operating Account - BDO Unibank, Inc.,PHP
"""

import base64

# Upload CSV file via base64 upload_file
b64_data = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
upload_payload = {
    "filename": "bdo_statement_sept_2026.csv",
    "filedata": b64_data,
    "is_private": 1
}

upload_res = call("/api/method/upload_file", "POST", upload_payload)
file_url = upload_res.get("message", {}).get("file_url")
print(f"[OK] Uploaded Bank Statement CSV: {file_url}")


# Process and import bank statement transactions via Server Script
import_statement_script = f"""
file_url = "{file_url}"
ba_name = "Automan Operating Account - BDO Unibank, Inc."

# Parse CSV rows
lines = \"\"\"{csv_content.strip()}\"\"\".split("\\n")
headers = [h.strip() for h in lines[0].split(",")]

created_txns = []
for line in lines[1:]:
    if not line.strip():
        continue
    parts = [p.strip() for p in line.split(",")]
    row = dict(zip(headers, parts))
    
    dep = frappe.utils.flt(row.get("Deposit") or 0)
    wdr = frappe.utils.flt(row.get("Withdrawal") or 0)
    
    bt = frappe.get_doc({{
        "doctype": "Bank Transaction",
        "bank_account": ba_name,
        "company": "Automan Car Care Center",
        "date": row.get("Date"),
        "deposit": dep,
        "withdrawal": wdr,
        "currency": "PHP",
        "description": row.get("Description"),
        "reference_number": row.get("Reference Number"),
        "transaction_id": row.get("Reference Number")
    }})
    bt.insert(ignore_permissions=True)
    bt.submit()
    created_txns.append({{
        "name": bt.name,
        "date": str(bt.date),
        "deposit": bt.deposit,
        "withdrawal": bt.withdrawal,
        "description": bt.description,
        "status": bt.status,
        "unallocated_amount": bt.unallocated_amount
    }})

frappe.response["message"] = {{
    "imported_count": len(created_txns),
    "transactions": created_txns
}}
"""

ss = {
    "name": "VM Process Bank Statement Upload",
    "doctype": "Server Script",
    "script_type": "API",
    "api_method": "vm_process_bank_statement_upload",
    "allow_guest": 0,
    "disabled": 0,
    "script": import_statement_script
}

chk = call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Process Bank Statement Upload')}", "GET")
if chk.get("data"):
    call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Process Bank Statement Upload')}", "PUT", {"script": import_statement_script, "disabled": 0})
else:
    call("/api/resource/Server%20Script", "POST", ss)

print("[Executing Bank Statement Upload & Transaction Generation...]")
res_import = call("/api/method/vm_process_bank_statement_upload", "POST", {})
print("\nImported Bank Statement Result:")
print(json.dumps(res_import, indent=2))

# Cleanup temporary import script
call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Process Bank Statement Upload')}", "DELETE")
