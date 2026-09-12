import urllib.request
import urllib.parse
import json
import http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json'
}

data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H))

vm_script = """
if doc.make:
    clean_make = doc.make.strip().upper()
    existing_make = frappe.db.get_value("Vehicle Make", {"name": ["ilike", clean_make]}, "name")
    if existing_make:
        doc.make = existing_make
    else:
        if not frappe.db.exists("Vehicle Make", clean_make):
            try:
                mk = frappe.get_doc({"doctype": "Vehicle Make", "name": clean_make, "make_name": clean_make})
                mk.insert(ignore_permissions=True)
            except Exception:
                pass
        doc.make = clean_make

if doc.model_name:
    doc.model_name = doc.model_name.strip().upper()

if not doc.make or not doc.model_name:
    frappe.throw("Both Make and Model Name are required.", title="Missing Fields")

# Check for existing duplicate under the same Make
existing = frappe.db.sql('''
    SELECT name FROM "tabVehicle Model"
    WHERE UPPER(TRIM(make)) = %s 
      AND UPPER(TRIM(model_name)) = %s 
      AND name != %s
    LIMIT 1
''', (doc.make, doc.model_name, doc.name or ""), as_dict=True)

if existing:
    frappe.throw(
        f"Vehicle Model '{doc.model_name}' already exists for Make '{doc.make}' (Existing Record: {existing[0]['name']}). Duplicate vehicle models are not allowed.",
        title="Duplicate Vehicle Model"
    )
"""

item_script = """
if doc.item_code:
    doc.item_code = doc.item_code.strip().upper()
if doc.item_name:
    doc.item_name = doc.item_name.strip().upper()
if doc.item_group:
    doc.item_group = doc.item_group.strip().upper()
if doc.brand:
    doc.brand = doc.brand.strip().upper()
if doc.description and not str(doc.description).startswith("http"):
    doc.description = str(doc.description).upper()
"""

cust_script = """
if doc.customer_name:
    doc.customer_name = doc.customer_name.strip().upper()
if doc.customer_group:
    doc.customer_group = doc.customer_group.strip().upper()
if doc.territory:
    doc.territory = doc.territory.strip().upper()
if doc.tax_id:
    doc.tax_id = doc.tax_id.strip().upper()
"""

veh_script = """
if doc.make:
    clean_make = doc.make.strip().upper()
    existing_make = frappe.db.get_value("Vehicle Make", {"name": ["ilike", clean_make]}, "name")
    doc.make = existing_make if existing_make else clean_make

if doc.model:
    clean_model = doc.model.strip().upper()
    existing_model = frappe.db.get_value("Vehicle Model", {"name": ["ilike", clean_model]}, "name")
    doc.model = existing_model if existing_model else clean_model

if doc.plate_no:
    doc.plate_no = doc.plate_no.strip().upper()
if doc.chassis_no:
    doc.chassis_no = doc.chassis_no.strip().upper()
if doc.engine_no:
    doc.engine_no = doc.engine_no.strip().upper()
if doc.color:
    doc.color = doc.color.strip().upper()
"""

supp_script = """
if doc.supplier_name:
    doc.supplier_name = doc.supplier_name.strip().upper()
if doc.supplier_group:
    doc.supplier_group = doc.supplier_group.strip().upper()
if doc.tax_id:
    doc.tax_id = doc.tax_id.strip().upper()
"""

def save_script(name, payload):
    req_put = urllib.request.Request(
        f'{URL}/api/resource/Server%20Script/{urllib.parse.quote(name)}',
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'},
        method='PUT'
    )
    try:
        op.open(req_put)
    except Exception:
        req_post = urllib.request.Request(
            f'{URL}/api/resource/Server%20Script',
            data=json.dumps(payload).encode(),
            headers={'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'},
            method='POST'
        )
        op.open(req_post)

# Register both Before Insert and Before Save events for maximum coverage
configs = [
    ('VM Validate Vehicle Model', 'Vehicle Model', 'Before Insert', vm_script),
    ('VM Validate Vehicle Model Save', 'Vehicle Model', 'Before Save', vm_script),
    ('VM Validate Item Master', 'Item', 'Before Insert', item_script),
    ('VM Validate Item Master Save', 'Item', 'Before Save', item_script),
    ('VM Validate Customer Master', 'Customer', 'Before Insert', cust_script),
    ('VM Validate Customer Master Save', 'Customer', 'Before Save', cust_script),
    ('VM Validate Customer Vehicle', 'Customer Vehicle', 'Before Insert', veh_script),
    ('VM Validate Customer Vehicle Save', 'Customer Vehicle', 'Before Save', veh_script),
    ('VM Validate Supplier Master', 'Supplier', 'Before Insert', supp_script),
    ('VM Validate Supplier Master Save', 'Supplier', 'Before Save', supp_script),
]

for name, dt, ev, sc in configs:
    save_script(name, {
        'doctype': 'Server Script',
        'name': name,
        'script_type': 'DocType Event',
        'reference_doctype': dt,
        'doctype_event': ev,
        'allow_guest': 1,
        'disabled': 0,
        'script': sc
    })
    print(f"Configured {name} ({dt} - {ev})")

print("All Before Insert & Before Save event scripts deployed successfully!")
