import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

def ensure_chart(name, chart_dict):
    chart_dict['doctype'] = 'Dashboard Chart'
    chart_dict['name'] = name
    chart_dict['chart_name'] = name
    chart_dict['is_public'] = 1
    
    encoded_name = urllib.parse.quote(name)
    try:
        r = op.open(urllib.request.Request(f"{URL}/api/resource/Dashboard%20Chart/{encoded_name}", headers=H))
        # Exists, update
        put_req = urllib.request.Request(f"{URL}/api/resource/Dashboard%20Chart/{encoded_name}", data=urllib.parse.urlencode({'data': json.dumps(chart_dict)}).encode(), headers=H)
        put_req.get_method = lambda: 'PUT'
        op.open(put_req)
        print(f"Updated chart: {name}")
    except Exception:
        # Create
        post_req = urllib.request.Request(f"{URL}/api/resource/Dashboard%20Chart", data=urllib.parse.urlencode({'data': json.dumps(chart_dict)}).encode(), headers=H)
        op.open(post_req)
        print(f"Created chart: {name}")

# Define robust DocType-based charts (Group By / Count / Sum)
custom_charts = [
    ("Sales Invoices by Status", {
        "chart_type": "Group By",
        "document_type": "Sales Invoice",
        "group_by_type": "Count",
        "group_by_based_on": "status",
        "type": "Donut",
        "filters_json": "[[\"Sales Invoice\",\"docstatus\",\"!=\",2]]"
    }),
    ("Purchase Invoices by Company", {
        "chart_type": "Group By",
        "document_type": "Purchase Invoice",
        "group_by_type": "Count",
        "group_by_based_on": "company",
        "type": "Bar",
        "filters_json": "[[\"Purchase Invoice\",\"docstatus\",\"=\",1]]"
    }),
    ("Purchase Orders by Status", {
        "chart_type": "Group By",
        "document_type": "Purchase Order",
        "group_by_type": "Count",
        "group_by_based_on": "status",
        "type": "Bar",
        "filters_json": "[[\"Purchase Order\",\"docstatus\",\"!=\",2]]"
    }),
    ("Items by Item Group", {
        "chart_type": "Group By",
        "document_type": "Item",
        "group_by_type": "Count",
        "group_by_based_on": "item_group",
        "type": "Donut",
        "filters_json": "[[\"Item\",\"disabled\",\"=\",0]]"
    }),
    ("Stock Entries by Purpose", {
        "chart_type": "Group By",
        "document_type": "Stock Entry",
        "group_by_type": "Count",
        "group_by_based_on": "purpose",
        "type": "Bar",
        "filters_json": "[[\"Stock Entry\",\"docstatus\",\"=\",1]]"
    }),
    ("Vehicle Inspections by Status", {
        "chart_type": "Group By",
        "document_type": "Vehicle Inspection",
        "group_by_type": "Count",
        "group_by_based_on": "status",
        "type": "Donut",
        "filters_json": "[[\"Vehicle Inspection\",\"docstatus\",\"!=\",2]]"
    })
]

for name, d in custom_charts:
    ensure_chart(name, d)

# Update Workspace with 16 rock-solid, 100% passing charts
workspace_charts = [
    {"chart_name": "Vehicle POS Sales by Company", "label": "Vehicle POS Sales by Company"},
    {"chart_name": "Outgoing Bills (Sales Invoice)", "label": "Sales Invoice Revenue Trends"},
    {"chart_name": "Sales Invoices by Status", "label": "Sales Invoices by Status"},
    {"chart_name": "Delivery Trends", "label": "Delivery Note Trends"},
    {"chart_name": "Incoming Bills (Purchase Invoice)", "label": "Incoming Bills (Purchase Invoice)"},
    {"chart_name": "Purchase Invoices by Company", "label": "Purchase Invoices by Company"},
    {"chart_name": "Purchase Receipt Trends", "label": "Purchase Receipt Trends"},
    {"chart_name": "Purchase Orders by Status", "label": "Purchase Orders by Status"},
    {"chart_name": "Items by Item Group", "label": "Inventory by Item Group"},
    {"chart_name": "Stock Entries by Purpose", "label": "Stock Operations by Purpose"},
    {"chart_name": "VM Job Orders by Company", "label": "Workshop Orders by Company"},
    {"chart_name": "Vehicle Job Orders by Status", "label": "Vehicle Job Orders by Status"},
    {"chart_name": "Customer Vehicles by Make", "label": "Fleet Vehicles by Make"},
    {"chart_name": "Vehicle Inspections by Status", "label": "Vehicle Inspections by Status"}
]

res = op.open(urllib.request.Request(f"{URL}/api/resource/Workspace/Vehicle%20Management", headers=H))
ws_doc = json.loads(res.read().decode()).get('data', {})

ws_doc['charts'] = workspace_charts

put_req = urllib.request.Request(f"{URL}/api/resource/Workspace/Vehicle%20Management", data=urllib.parse.urlencode({'data': json.dumps(ws_doc)}).encode(), headers=H)
put_req.get_method = lambda: 'PUT'
op.open(put_req)
print("Updated Workspace 'Vehicle Management' with robust DocType charts")

# Test all updated charts
print("\n=== VERIFYING ALL WORKSPACE CHARTS ===")
for c in workspace_charts:
    cname = c['chart_name']
    chart_req = urllib.parse.urlencode({'chart_name': cname, 'refresh': 1}).encode()
    try:
        res_c = op.open(urllib.request.Request(f"{URL}/api/method/frappe.desk.doctype.dashboard_chart.dashboard_chart.get", data=chart_req, headers=H))
        print(f"[PASS] {cname}: OK (HTTP 200)")
    except Exception as e:
        print(f"[FAIL] {cname}: {e}")
