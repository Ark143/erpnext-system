import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def api_post(endpoint, payload):
    req_data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(f'http://38.247.138.224:10017{endpoint}', data=req_data, headers=H)
    r = op.open(req)
    return json.loads(r.read().decode())

def create_or_update_custom_field(field_def):
    name = f"{field_def['dt']}-{field_def['fieldname']}"
    # Check if exists
    try:
        r = op.open(urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Custom%20Field/{urllib.parse.quote(name)}', headers=H))
        doc = json.loads(r.read().decode())
        print(f"Custom Field {name} already exists, updating...")
        req = urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Custom%20Field/{urllib.parse.quote(name)}', data=urllib.parse.urlencode({'data': json.dumps(field_def)}).encode(), headers=H)
        req.get_method = lambda: 'PUT'
        res = op.open(req)
        print("Updated:", name)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Creating Custom Field {name}...")
            req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Custom%20Field', data=urllib.parse.urlencode({'data': json.dumps(field_def)}).encode(), headers=H)
            res = op.open(req)
            print("Created:", name)
        else:
            raise

fields = [
    {
        "dt": "Stock Entry",
        "fieldname": "custom_receiver_section",
        "label": "Receiver Safety & Verification Check",
        "fieldtype": "Section Break",
        "insert_after": "scan_barcode",
        "collapsible": 0,
        "depends_on": "eval:doc.stock_entry_type == 'Material Issue'"
    },
    {
        "dt": "Stock Entry",
        "fieldname": "custom_receiver_btn_html",
        "label": "Verification Action",
        "fieldtype": "HTML",
        "insert_after": "custom_receiver_section",
        "depends_on": "eval:doc.stock_entry_type == 'Material Issue'"
    },
    {
        "dt": "Stock Entry",
        "fieldname": "custom_receiver_user",
        "label": "Receiver User ID",
        "fieldtype": "Link",
        "options": "User",
        "insert_after": "custom_receiver_btn_html",
        "read_only": 1,
        "in_list_view": 1,
        "in_standard_filter": 1,
        "depends_on": "eval:doc.stock_entry_type == 'Material Issue'"
    },
    {
        "dt": "Stock Entry",
        "fieldname": "custom_receiver_employee",
        "label": "Receiver Employee ID",
        "fieldtype": "Link",
        "options": "Employee",
        "insert_after": "custom_receiver_user",
        "read_only": 1,
        "in_list_view": 1,
        "depends_on": "eval:doc.stock_entry_type == 'Material Issue'"
    },
    {
        "dt": "Stock Entry",
        "fieldname": "custom_receiver_name",
        "label": "Receiver Employee Name",
        "fieldtype": "Data",
        "insert_after": "custom_receiver_employee",
        "read_only": 1,
        "in_list_view": 1,
        "depends_on": "eval:doc.stock_entry_type == 'Material Issue'"
    },
    {
        "dt": "Stock Entry",
        "fieldname": "custom_receiver_col_break",
        "fieldtype": "Column Break",
        "insert_after": "custom_receiver_name",
        "depends_on": "eval:doc.stock_entry_type == 'Material Issue'"
    },
    {
        "dt": "Stock Entry",
        "fieldname": "custom_receiver_photo",
        "label": "Receiver / Handover Photo",
        "fieldtype": "Attach Image",
        "insert_after": "custom_receiver_col_break",
        "depends_on": "eval:doc.stock_entry_type == 'Material Issue'"
    },
    {
        "dt": "Stock Entry",
        "fieldname": "custom_receiver_verified_at",
        "label": "Verified At",
        "fieldtype": "Datetime",
        "insert_after": "custom_receiver_photo",
        "read_only": 1,
        "depends_on": "eval:doc.stock_entry_type == 'Material Issue'"
    },
    {
        "dt": "Stock Entry",
        "fieldname": "custom_receiver_verified_by_qr",
        "label": "Verified via QR Scan",
        "fieldtype": "Check",
        "default": "0",
        "insert_after": "custom_receiver_verified_at",
        "read_only": 1,
        "depends_on": "eval:doc.stock_entry_type == 'Material Issue'"
    }
]

for f in fields:
    create_or_update_custom_field(f)

print("All Custom Fields for Stock Entry created/updated successfully!")
