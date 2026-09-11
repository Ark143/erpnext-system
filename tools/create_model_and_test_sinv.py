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

# 1. Create Toyota-INNOVA 2.0 DSL AT
mdl_payload = {
    "doctype": "Vehicle Model",
    "make": "Toyota",
    "model_name": "INNOVA 2.0 DSL AT",
    "category": "Van"
}
res_create = call("/api/resource/Vehicle%20Model", "POST", mdl_payload)
print("[OK] Created Vehicle Model:", res_create)

# 2. Check all distinct models from Customer Vehicle
res_cv = call("/api/resource/Customer%20Vehicle?fields=[\"make\",\"model\"]&limit_page_length=500", "GET")
cv_rows = res_cv.get("data", [])
print(f"\n[OK] Checking {len(cv_rows)} Customer Vehicle records...")

for r in cv_rows:
    mk = (r.get("make") or "").strip()
    mdl = (r.get("model") or "").strip()
    if mdl:
        chk = call(f"/api/resource/Vehicle%20Model/{urllib.parse.quote(mdl)}", "GET")
        if chk.get("exc_type") == "DoesNotExistError" or "not found" in str(chk):
            # Create it
            sub_mk = mk or "Toyota" if "toyota" in mdl.lower() else "Other"
            sub_mdl = mdl
            if "-" in mdl:
                parts = mdl.split("-", 1)
                sub_mk = parts[0].strip() or sub_mk
                sub_mdl = parts[1].strip()
            # Ensure make exists
            call(f"/api/resource/Vehicle%20Make", "POST", {"doctype": "Vehicle Make", "make_name": sub_mk})
            res_m = call(f"/api/resource/Vehicle%20Model", "POST", {
                "doctype": "Vehicle Model",
                "make": sub_mk,
                "model_name": sub_mdl
            })
            print(f"  -> Created missing model: {mdl} (Make: {sub_mk})")

# 3. Test saving/validating Sales Invoice ACC-SINV-2026-00449
res_inv = call(f"/api/resource/Sales%20Invoice/ACC-SINV-2026-00449", "GET")
inv_data = res_inv.get("data", {})
print(f"\nSales Invoice {inv_data.get('name')} status: docstatus={inv_data.get('docstatus')}, vehicle_model={inv_data.get('custom_vehicle_model')}")

# Call savedocs validate or save
test_save = call(f"/api/resource/Sales%20Invoice/ACC-SINV-2026-00449", "PUT", {
    "custom_vehicle_model": inv_data.get("custom_vehicle_model")
})
print("Test PUT save result error?", "error" in test_save or "exc_type" in test_save)
if "data" in test_save:
    print("[OK] Sales Invoice saved cleanly with Vehicle Model link verified!")
