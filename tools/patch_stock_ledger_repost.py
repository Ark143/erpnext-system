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

# Patch stock_ledger.py on VPS
patch_script = """
sl = frappe.get_module("erpnext.stock.stock_ledger")
sc = frappe.get_module("erpnext.controllers.stock_controller")

def get_items_to_be_repost(voucher_type=None, voucher_no=None, doc=None, reposting_data=None):
    if reposting_data and getattr(reposting_data, "items_to_be_repost", None):
        return reposting_data.items_to_be_repost

    items_to_be_repost = []

    if doc and getattr(doc, "items_to_be_repost", None):
        items_to_be_repost = frappe.parse_json(doc.items_to_be_repost)

    if not items_to_be_repost and voucher_type and voucher_no:
        items_to_be_repost = frappe.db.get_all(
            "Stock Ledger Entry",
            filters={"voucher_type": voucher_type, "voucher_no": voucher_no},
            fields=["item_code", "warehouse", "posting_date", "posting_time", "creation", "posting_datetime"],
            order_by="creation asc",
        )

    return items_to_be_repost or []

# Monkeypatch in memory across modules
sl.get_items_to_be_repost = get_items_to_be_repost
sc.get_items_to_be_repost = get_items_to_be_repost

# Update on disk permanently
disk_updated = False
try:
    filepath = frappe.get_app_path("erpnext", "stock", "stock_ledger.py")
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
    
    if 'group_by="item_code, warehouse"' in code:
        code = code.replace('group_by="item_code, warehouse",', '')
        code = code.replace('group_by="item_code, warehouse"', '')
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        disk_updated = True
    else:
        disk_updated = "Already patched or pattern not found"
except Exception as e:
    disk_updated = "Error: " + str(e)

frappe.response["message"] = {
    "status": "success",
    "disk_updated": disk_updated
}
"""


ss_patch = {
    "name": "VM Patch Stock Ledger Group By",
    "doctype": "Server Script",
    "script_type": "API",
    "api_method": "vm_patch_stock_ledger_group_by",
    "allow_guest": 0,
    "disabled": 0,
    "script": patch_script
}

chk = call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Patch Stock Ledger Group By')}", "GET")
if chk.get("data"):
    call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Patch Stock Ledger Group By')}", "PUT", {"script": patch_script, "disabled": 0})
else:
    call("/api/resource/Server%20Script", "POST", ss_patch)

print("[Applying Stock Ledger Patch on VPS...]")
res = call("/api/method/vm_patch_stock_ledger_group_by", "POST", {})
print("Patch result:", res)
