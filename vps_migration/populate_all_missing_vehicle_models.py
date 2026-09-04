import urllib.request, urllib.parse, json, http.cookiejar, sys

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
res = op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)
print("[OK] Logged into VPS successfully.")

# -------------------------------------------------------------
# 1. Fetch all distinct makes and models using Server Script
# -------------------------------------------------------------
script_code = """
rows = frappe.db.sql('''
    SELECT DISTINCT make, model 
    FROM `tabCustomer Vehicle` 
    WHERE model IS NOT NULL AND model != ''
''', as_dict=True)

frappe.response['message'] = rows
"""

script_payload = {
    "name": "VM Get Distinct Models",
    "script_type": "API",
    "api_method": "vm_get_distinct_models",
    "disabled": 0,
    "script": script_code
}

try:
    up_req = urllib.request.Request(f'{URL}/api/resource/Server%20Script/VM%20Get%20Distinct%20Models', data=json.dumps(script_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='PUT')
    op.open(up_req, timeout=15)
except Exception:
    create_req = urllib.request.Request(f'{URL}/api/resource/Server%20Script', data=json.dumps(script_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='POST')
    op.open(create_req, timeout=15)

# Call method
req_get = urllib.request.Request(f'{URL}/api/method/vm_get_distinct_models', headers=H)
res_get = op.open(req_get, timeout=30)
distinct_rows = json.loads(res_get.read().decode()).get('message', [])
print(f"[OK] Fetched {len(distinct_rows)} distinct vehicle models from database.")

# -------------------------------------------------------------
# 2. Get existing makes and models
# -------------------------------------------------------------
req_makes = urllib.request.Request(f'{URL}/api/resource/Vehicle%20Make?limit_page_length=500', headers=H)
res_makes = op.open(req_makes, timeout=15)
existing_makes = set(m['name'] for m in json.loads(res_makes.read().decode()).get('data', []))

req_models = urllib.request.Request(f'{URL}/api/resource/Vehicle%20Model?limit_page_length=5000', headers=H)
res_models = op.open(req_models, timeout=15)
existing_models = set(m['name'] for m in json.loads(res_models.read().decode()).get('data', []))

print(f"Existing Makes: {len(existing_makes)}, Existing Models: {len(existing_models)}")

# -------------------------------------------------------------
# 3. Create missing makes and models
# -------------------------------------------------------------
created_makes = 0
created_models = 0

for row in distinct_rows:
    raw_make = (row.get('make') or '').strip()
    raw_model = (row.get('model') or '').strip()
    if not raw_model:
        continue

    # Determine make
    # If model is prefixed like "TOYOTA-FORTUNER...", extract make
    make = raw_make
    model_name = raw_model

    if '-' in raw_model:
        parts = raw_model.split('-', 1)
        possible_make = parts[0].strip()
        possible_model = parts[1].strip()
        if not make:
            make = possible_make
        model_name = possible_model
    
    if not make:
        make = "Other"

    # Normalize make capitalization if known, or title case
    # If "TOYOTA" in existing_makes or "Toyota" in existing_makes
    make_match = None
    for em in existing_makes:
        if em.lower() == make.lower():
            make_match = em
            break
    
    if not make_match:
        make_match = make.title() if len(make) > 3 else make.upper()
        # Create make
        try:
            mk_payload = {"doctype": "Vehicle Make", "make_name": make_match}
            req_mk = urllib.request.Request(f'{URL}/api/resource/Vehicle%20Make', data=json.dumps(mk_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='POST')
            op.open(req_mk, timeout=10)
            existing_makes.add(make_match)
            created_makes += 1
        except Exception:
            existing_makes.add(make_match)

    # Check if raw_model or formatted model exists
    target_name = f"{make_match}-{model_name}"
    
    # We need to make sure both raw_model (what's stored in Customer Vehicle) and target_name exist
    if raw_model not in existing_models and target_name not in existing_models:
        try:
            # Create model
            mdl_payload = {
                "doctype": "Vehicle Model",
                "make": make_match,
                "model_name": model_name
            }
            req_mdl = urllib.request.Request(f'{URL}/api/resource/Vehicle%20Model', data=json.dumps(mdl_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='POST')
            res_mdl = op.open(req_mdl, timeout=10)
            created_data = json.loads(res_mdl.read().decode()).get('data', {})
            created_name = created_data.get('name')
            existing_models.add(created_name)
            existing_models.add(raw_model)
            created_models += 1
        except Exception as e:
            pass

print(f"\n[DONE] Successfully created {created_makes} new Makes and {created_models} new Vehicle Models.")
