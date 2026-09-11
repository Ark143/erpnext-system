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

# 1. Fetch all existing Vehicle Makes and Models into Sets
all_makes = set(m['name'] for m in call("/api/resource/Vehicle%20Make?limit_page_length=2000", "GET").get("data", []))
all_models = set(m['name'] for m in call("/api/resource/Vehicle%20Model?limit_page_length=5000", "GET").get("data", []))
print(f"[OK] Existing Makes in DB: {len(all_makes)}, Existing Models: {len(all_models)}")

# Check if Toyota-INNOVA 2.0 DSL AT is present
target_model = "Toyota-INNOVA 2.0 DSL AT"
if target_model not in all_models:
    res_t = call("/api/resource/Vehicle%20Model", "POST", {
        "doctype": "Vehicle Model",
        "make": "Toyota",
        "model_name": "INNOVA 2.0 DSL AT",
        "category": "Van"
    })
    print(f"  -> Created '{target_model}':", res_t.get("data", {}).get("name"))
    all_models.add(target_model)
else:
    print(f"  -> '{target_model}' already exists!")

# 2. Gather all distinct models from Customer Vehicle, Sales Invoice, Job Order
res_cv = call("/api/resource/Customer%20Vehicle?fields=[\"make\",\"model\"]&limit_page_length=1000", "GET")
cv_rows = res_cv.get("data", [])

missing_models = set()
for r in cv_rows:
    mdl = (r.get("model") or "").strip()
    mk = (r.get("make") or "").strip()
    if mdl and mdl not in all_models:
        missing_models.add((mk, mdl))

print(f"\n[OK] Found {len(missing_models)} missing models across Customer Vehicles to create...")

for mk, mdl in missing_models:
    sub_mk = mk or "Other"
    sub_mdl = mdl
    if "-" in mdl:
        parts = mdl.split("-", 1)
        sub_mk = parts[0].strip() or sub_mk
        sub_mdl = parts[1].strip()
        
    if sub_mk not in all_makes:
        call("/api/resource/Vehicle%20Make", "POST", {"doctype": "Vehicle Make", "make_name": sub_mk})
        all_makes.add(sub_mk)
        
    res_m = call("/api/resource/Vehicle%20Model", "POST", {
        "doctype": "Vehicle Model",
        "make": sub_mk,
        "model_name": sub_mdl
    })
    created_name = res_m.get("data", {}).get("name")
    if created_name:
        all_models.add(created_name)
        print(f"  -> Created model: {created_name}")

# 3. Test saving/validating Sales Invoice ACC-SINV-2026-00449
res_inv = call(f"/api/resource/Sales%20Invoice/ACC-SINV-2026-00449", "GET")
inv_data = res_inv.get("data", {})
print(f"\n[OK] Sales Invoice {inv_data.get('name')}:")
print(f"  Customer: {inv_data.get('customer')}")
print(f"  Vehicle Plate: {inv_data.get('custom_vehicle_plate')}")
print(f"  Vehicle Model: {inv_data.get('custom_vehicle_model')}")
print(f"  DocStatus: {inv_data.get('docstatus')}")

# Verify link
res_check = call(f"/api/resource/Vehicle%20Model/{urllib.parse.quote(inv_data.get('custom_vehicle_model'))}", "GET")
print(f"[OK] Link target exists in Vehicle Model: {res_check.get('data', {}).get('name')}")
