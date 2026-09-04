import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

shortcuts = [
    # ── 1. Operations & Workshop
    {
        "label": "Vehicle POS Terminal",
        "type": "Page",
        "link_to": "vehicle_pos",
        "color": "Green"
    },
    {
        "label": "Customer Vehicles",
        "type": "DocType",
        "link_to": "Customer Vehicle",
        "doc_view": "List",
        "color": "Blue"
    },
    {
        "label": "Vehicle Job Orders",
        "type": "DocType",
        "link_to": "Vehicle Job Order",
        "doc_view": "List",
        "color": "Orange"
    },
    {
        "label": "Vehicle Inspections",
        "type": "DocType",
        "link_to": "Vehicle Inspection",
        "doc_view": "List",
        "color": "Purple"
    },
    {
        "label": "Vehicle Estimates",
        "type": "DocType",
        "link_to": "Vehicle Estimate",
        "doc_view": "List",
        "color": "Grey"
    },
    {
        "label": "Service Reminders",
        "type": "DocType",
        "link_to": "Vehicle Service Reminder",
        "doc_view": "List",
        "color": "Red"
    },

    # ── 2. Point of Sale & Invoicing
    {
        "label": "POS Invoices",
        "type": "DocType",
        "link_to": "POS Invoice",
        "doc_view": "List",
        "color": "Green"
    },
    {
        "label": "Sales Invoices",
        "type": "DocType",
        "link_to": "Sales Invoice",
        "doc_view": "List",
        "color": "Blue"
    },
    {
        "label": "Payment Entries",
        "type": "DocType",
        "link_to": "Payment Entry",
        "doc_view": "List",
        "color": "Teal"
    },

    # ── 3. Procurement & Stock
    {
        "label": "Auto Parts Catalog",
        "type": "DocType",
        "link_to": "Item",
        "doc_view": "List",
        "color": "Grey"
    },
    {
        "label": "Purchase Orders",
        "type": "DocType",
        "link_to": "Purchase Order",
        "doc_view": "List",
        "color": "Purple"
    },
    {
        "label": "Purchase Receipts",
        "type": "DocType",
        "link_to": "Purchase Receipt",
        "doc_view": "List",
        "color": "Cyan"
    },

    # ── 4. Key Analytical Reports
    {
        "label": "Stock Balance",
        "type": "Report",
        "link_to": "Stock Balance",
        "report_ref_doctype": "Stock Ledger Entry",
        "color": "Green"
    },
    {
        "label": "Monthly Sales Report",
        "type": "Report",
        "link_to": "Monthly Sales Report",
        "report_ref_doctype": "Sales Invoice",
        "color": "Orange"
    },
    {
        "label": "Profit & Loss",
        "type": "Report",
        "link_to": "Profit and Loss Statement",
        "report_ref_doctype": "GL Entry",
        "color": "Teal"
    },
    {
        "label": "General Ledger",
        "type": "Report",
        "link_to": "General Ledger",
        "report_ref_doctype": "GL Entry",
        "color": "Blue"
    }
]

res = op.open(urllib.request.Request(f"{URL}/api/resource/Workspace/Vehicle%20Management", headers=H))
ws_doc = json.loads(res.read().decode()).get('data', {})

ws_doc['shortcuts'] = shortcuts

put_req = urllib.request.Request(
    f"{URL}/api/resource/Workspace/Vehicle%20Management",
    data=urllib.parse.urlencode({'data': json.dumps(ws_doc)}).encode(),
    headers=H
)
put_req.get_method = lambda: 'PUT'
op.open(put_req)
print(f"Restored {len(shortcuts)} important shortcuts in Workspace 'Vehicle Management'!")

# Verify
res_verify = op.open(urllib.request.Request(f"{URL}/api/resource/Workspace/Vehicle%20Management", headers=H))
ws_updated = json.loads(res_verify.read().decode()).get('data', {})
print("\n=== VERIFIED SHORTCUTS LIST ===")
for s in ws_updated.get('shortcuts', []):
    print(f" - [{s.get('color', 'Default')}] {s.get('label')} ({s.get('type')}: {s.get('link_to') or s.get('url')})")
