import urllib.request, urllib.parse, json, http.cookiejar, sys

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
res = op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)
print("[OK] Logged in successfully.")

# -------------------------------------------------------------
# 1. Server Script to scan all distinct (make, model) from Customer Vehicle
#    and auto-create missing Vehicle Make & Vehicle Model records
# -------------------------------------------------------------
sync_script = """
# 1. Fetch all distinct make & model
distinct_models = frappe.db.sql('''
    SELECT DISTINCT make, model 
    FROM `tabCustomer Vehicle` 
    WHERE model IS NOT NULL AND model != ''
''', as_dict=True)

# Also fetch all distinct make from Customer Vehicle
distinct_makes = frappe.db.sql('''
    SELECT DISTINCT make 
    FROM `tabCustomer Vehicle` 
    WHERE make IS NOT NULL AND make != ''
''', as_dict=True)

existing_makes = set(frappe.db.sql_list('SELECT name FROM `tabVehicle Make`'))
existing_models = set(frappe.db.sql_list('SELECT name FROM `tabVehicle Model`'))

makes_created = 0
for row in distinct_makes:
    mk = (row.get('make') or '').strip()
    if mk and mk not in existing_makes:
        try:
            doc = frappe.get_doc({
                'doctype': 'Vehicle Make',
                'make_name': mk,
                'name': mk
            })
            doc.insert(ignore_permissions=True)
            existing_makes.add(mk)
            makes_created += 1
        except Exception as e:
            pass

models_created = 0
for row in distinct_models:
    mdl = (row.get('model') or '').strip()
    mk = (row.get('make') or '').strip() or 'Other'
    
    # Ensure make exists
    if mk not in existing_makes:
        try:
            doc_mk = frappe.get_doc({
                'doctype': 'Vehicle Make',
                'make_name': mk,
                'name': mk
            })
            doc_mk.insert(ignore_permissions=True)
            existing_makes.add(mk)
            makes_created += 1
        except Exception:
            pass
            
    if mdl and mdl not in existing_models:
        try:
            doc_m = frappe.get_doc({
                'doctype': 'Vehicle Model',
                'make': mk,
                'model_name': mdl,
                'name': mdl
            })
            doc_m.insert(ignore_permissions=True)
            existing_models.add(mdl)
            models_created += 1
        except Exception as e:
            pass

frappe.response['message'] = {
    'total_distinct_models': len(distinct_models),
    'makes_created': makes_created,
    'models_created': models_created,
    'total_existing_models': len(existing_models)
}
"""

script_name = "VM Sync Vehicle Models and Makes"
script_payload = {
    "name": script_name,
    "script_type": "API",
    "api_method": "vm_sync_vehicle_models",
    "disabled": 0,
    "script": sync_script
}

try:
    up_req = urllib.request.Request(f'{URL}/api/resource/Server%20Script/{urllib.parse.quote(script_name)}', data=json.dumps(script_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='PUT')
    op.open(up_req, timeout=15)
except Exception:
    create_req = urllib.request.Request(f'{URL}/api/resource/Server%20Script', data=json.dumps(script_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='POST')
    op.open(create_req, timeout=15)

# Run sync method
print("Running sync for all vehicle models & makes...")
test_req = urllib.request.Request(f'{URL}/api/method/vm_sync_vehicle_models', headers=H)
res = op.open(test_req, timeout=60)
result = json.loads(res.read().decode())
print("Sync Result:", json.dumps(result.get('message', {}), indent=2))
