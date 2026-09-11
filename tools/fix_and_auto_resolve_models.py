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

# 1. First, create Server Script to sweep and insert missing Vehicle Makes and Vehicle Models
sync_script = """
def auto_create_make_and_model(make_name, model_name):
    if not make_name:
        make_name = "Other"
    make_name = make_name.strip()
    
    if make_name and not frappe.db.exists("Vehicle Make", make_name):
        try:
            m = frappe.get_doc({
                "doctype": "Vehicle Make",
                "make_name": make_name,
                "name": make_name
            })
            m.insert(ignore_permissions=True)
        except Exception:
            pass
            
    if model_name:
        model_name = model_name.strip()
        if not frappe.db.exists("Vehicle Model", model_name):
            try:
                # determine make and clean model
                sub_make = make_name
                sub_model = model_name
                if "-" in model_name:
                    parts = model_name.split("-", 1)
                    if not make_name or make_name == "Other":
                        sub_make = parts[0].strip()
                    sub_model = parts[1].strip()
                    
                md = frappe.get_doc({
                    "doctype": "Vehicle Model",
                    "name": model_name,
                    "make": sub_make,
                    "model_name": sub_model
                })
                md.insert(ignore_permissions=True)
            except Exception:
                pass

# Sweep all tables with vehicle info
tables = [
    ("tabCustomer Vehicle", "make", "model"),
    ("tabSales Invoice", "custom_vehicle_make", "custom_vehicle_model"),
    ("tabSales Invoice", "vehicle_make", "vehicle_model"),
    ("tabVehicle Job Order", "make", "model"),
    ("tabVehicle Job Order", "vehicle_make", "vehicle_model"),
    ("tabVehicle Estimate", "make", "model"),
    ("tabQuotation", "custom_vehicle_make", "custom_vehicle_model"),
    ("tabSales Order", "custom_vehicle_make", "custom_vehicle_model"),
    ("tabDelivery Note", "custom_vehicle_make", "custom_vehicle_model"),
    ("tabPOS Invoice", "custom_vehicle_make", "custom_vehicle_model"),
    ("tabVehicle POS Invoice", "vehicle_make", "vehicle_model"),
]

created = []
for tbl, mk_col, mdl_col in tables:
    try:
        rows = frappe.db.sql(f'''
            SELECT DISTINCT {mk_col} as make, {mdl_col} as model
            FROM `{tbl}`
            WHERE {mdl_col} IS NOT NULL AND {mdl_col} != ''
        ''', as_dict=True)
        for r in rows:
            mk = r.get("make") or ""
            mdl = r.get("model") or ""
            if mdl:
                auto_create_make_and_model(mk, mdl)
                created.append({"make": mk, "model": mdl})
    except Exception:
        pass

# Ensure 'Toyota-INNOVA 2.0 DSL AT' explicitly exists
auto_create_make_and_model("Toyota", "Toyota-INNOVA 2.0 DSL AT")

frappe.response["message"] = {"status": "success", "processed_records": len(created)}
"""

# Deploy runner server script
ss_sync = {
    'name': 'VM Sync All Vehicle Models Now',
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_sync_all_models_now',
    'allow_guest': 0,
    'disabled': 0,
    'script': sync_script
}

try:
    call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Sync All Vehicle Models Now')}", "PUT", {"script": sync_script})
except Exception:
    call("/api/resource/Server%20Script", "POST", ss_sync)

res_sync = call("/api/method/vm_sync_all_models_now", "POST", {})
print("[OK] Sync all models response:", res_sync)

# 2. Deploy universal DocType Events to auto-create Vehicle Make/Model Before Validate on ALL vehicle transactions
auto_resolve_code = """
make = doc.get("make") or doc.get("custom_vehicle_make") or doc.get("vehicle_make") or ""
model = doc.get("model") or doc.get("custom_vehicle_model") or doc.get("vehicle_model") or ""

if make:
    make = make.strip()
    if not frappe.db.exists("Vehicle Make", make):
        try:
            frappe.get_doc({
                "doctype": "Vehicle Make",
                "make_name": make,
                "name": make
            }).insert(ignore_permissions=True)
        except Exception:
            pass

if model:
    model = model.strip()
    if not frappe.db.exists("Vehicle Model", model):
        try:
            sub_make = make or "Other"
            sub_model = model
            if "-" in model:
                parts = model.split("-", 1)
                if not make or make == "Other":
                    sub_make = parts[0].strip()
                sub_model = parts[1].strip()
                
            frappe.get_doc({
                "doctype": "Vehicle Model",
                "name": model,
                "make": sub_make,
                "model_name": sub_model
            }).insert(ignore_permissions=True)
        except Exception:
            pass
"""

doctypes_to_hook = [
    "Sales Invoice",
    "Vehicle Job Order",
    "Customer Vehicle",
    "Vehicle Estimate",
    "Vehicle Inspection",
    "Quotation",
    "Sales Order",
    "Delivery Note",
    "POS Invoice",
    "Vehicle POS Invoice"
]

for dt in doctypes_to_hook:
    script_name = f"VM Auto Resolve Model on {dt}"
    payload = {
        "name": script_name,
        "doctype": "Server Script",
        "script_type": "DocType Event",
        "reference_doctype": dt,
        "doctype_event": "Before Validate",
        "disabled": 0,
        "script": auto_resolve_code
    }
    
    # Check if exists
    res_chk = call(f"/api/resource/Server%20Script/{urllib.parse.quote(script_name)}", "GET")
    if res_chk and not res_chk.get("error") and res_chk.get("data"):
        call(f"/api/resource/Server%20Script/{urllib.parse.quote(script_name)}", "PUT", {"script": auto_resolve_code, "disabled": 0})
        print(f"  [OK] Updated Server Script: {script_name}")
    else:
        call("/api/resource/Server%20Script", "POST", payload)
        print(f"  [OK] Created Server Script: {script_name}")

# 3. Verify Toyota-INNOVA 2.0 DSL AT exists in Vehicle Model
res_check = call(f"/api/resource/Vehicle%20Model/{urllib.parse.quote('Toyota-INNOVA 2.0 DSL AT')}", "GET")
print("\n[OK] Checked 'Toyota-INNOVA 2.0 DSL AT':", res_check.get("data", {}).get("name"))

# 4. Test submitting Sales Invoice ACC-SINV-2026-00449 (or saving it)
res_inv = call(f"/api/resource/Sales%20Invoice/ACC-SINV-2026-00449", "GET")
print("Invoice status before submit:", res_inv.get("data", {}).get("docstatus"), res_inv.get("data", {}).get("name"))
