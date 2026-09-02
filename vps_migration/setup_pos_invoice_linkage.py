import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def save_custom_field(cf_name, cf_data):
    try:
        r = op.open(urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Custom%20Field/{urllib.parse.quote(cf_name)}', headers=H))
        print(f"Custom Field '{cf_name}' already exists.")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            payload = dict(cf_data)
            payload['name'] = cf_name
            payload['doctype'] = 'Custom Field'
            req = urllib.request.Request(
                'http://38.247.138.224:10017/api/resource/Custom%20Field',
                data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(),
                headers=H
            )
            op.open(req)
            print(f"Created Custom Field '{cf_name}'.")
        else:
            raise

# 1. Create Custom Fields on POS Invoice
fields = [
    {
        "name": "POS Invoice-custom_vehicle_section",
        "dt": "POS Invoice",
        "label": "Vehicle Information",
        "fieldname": "custom_vehicle_section",
        "fieldtype": "Section Break",
        "insert_after": "customer"
    },
    {
        "name": "POS Invoice-custom_vehicle_pos_invoice",
        "dt": "POS Invoice",
        "label": "Vehicle POS Invoice",
        "fieldname": "custom_vehicle_pos_invoice",
        "fieldtype": "Link",
        "options": "Vehicle POS Invoice",
        "insert_after": "custom_vehicle_section",
        "read_only": 1,
        "in_list_view": 1,
        "in_standard_filter": 1
    },
    {
        "name": "POS Invoice-custom_customer_vehicle",
        "dt": "POS Invoice",
        "label": "Customer Vehicle",
        "fieldname": "custom_customer_vehicle",
        "fieldtype": "Link",
        "options": "Customer Vehicle",
        "insert_after": "custom_vehicle_pos_invoice",
        "read_only": 1,
        "in_list_view": 1
    },
    {
        "name": "POS Invoice-custom_plate_no",
        "dt": "POS Invoice",
        "label": "Plate Number",
        "fieldname": "custom_plate_no",
        "fieldtype": "Data",
        "insert_after": "custom_customer_vehicle",
        "read_only": 1,
        "in_list_view": 1,
        "in_standard_filter": 1
    }
]

print("--- Creating Custom Fields on POS Invoice ---")
for f in fields:
    save_custom_field(f["name"], f)

# 2. Backfill existing POS Invoices
backfill_script = """
def backfill():
    # Link every POS Invoice to its Vehicle POS Invoice
    vpis = frappe.get_all(
        "Vehicle POS Invoice",
        fields=["name", "pos_invoice", "vehicle", "customer"]
    )
    updated = []
    for v in vpis:
        if v.pos_invoice and frappe.db.exists("POS Invoice", v.pos_invoice):
            plate = frappe.db.get_value("Customer Vehicle", v.vehicle, "license_plate") if v.vehicle else ""
            frappe.db.set_value("POS Invoice", v.pos_invoice, {
                "custom_vehicle_pos_invoice": v.name,
                "custom_customer_vehicle": v.vehicle or "",
                "custom_plate_no": plate or ""
            }, update_modified=False)
            updated.append({"pos_invoice": v.pos_invoice, "vehicle_pos_invoice": v.name, "plate": plate})
            
    frappe.db.commit()
    frappe.response["message"] = {"status": "success", "updated": updated}

backfill()
"""

name = 'VM Backfill POS Invoice Links'
req = urllib.request.Request(
    f'http://38.247.138.224:10017/api/resource/Server%20Script/{urllib.parse.quote(name)}',
    data=urllib.parse.urlencode({'data': json.dumps({'script': backfill_script})}).encode(),
    headers=H
)
try:
    req.get_method = lambda: 'PUT'
    op.open(req)
except urllib.error.HTTPError:
    payload = {'name': name, 'doctype': 'Server Script', 'script_type': 'API', 'api_method': 'vm_backfill_pos_invoice_links', 'allow_guest': 1, 'disabled': 0, 'script': backfill_script}
    req = urllib.request.Request(
        'http://38.247.138.224:10017/api/resource/Server%20Script',
        data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(),
        headers=H
    )
    op.open(req)

r_backfill = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_backfill_pos_invoice_links', headers=H))
print("\n--- Backfill Result ---")
print(r_backfill.read().decode())
