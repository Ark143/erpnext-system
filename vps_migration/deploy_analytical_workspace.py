import urllib.request, urllib.parse, json, http.cookiejar, os

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

print("Logged in successfully as Administrator.")

# -------------------------------------------------------------
# 1. Update Workspace Sidebar: Vehicle Management
# -------------------------------------------------------------
sidebar_items = [
    # Main Links
    {"label": "Vehicle Management", "link_type": "Workspace", "type": "Link", "link_to": "Vehicle Management", "icon": "home"},
    {"label": "Vehicle POS Terminal", "link_type": "Page", "type": "Link", "link_to": "vehicle_pos", "icon": "panel-top"},
    {"label": "Vehicle Analytics", "link_type": "Page", "type": "Link", "link_to": "vehicle_analytics", "icon": "bar-chart"},

    # Operations & Workshop Section
    {"label": "Operations & Workshop", "type": "Section Break", "link_type": "DocType", "link_to": None, "icon": None},
    {"label": "Customer Vehicles", "link_type": "DocType", "type": "Link", "link_to": "Customer Vehicle", "icon": "car"},
    {"label": "Vehicle Job Orders", "link_type": "DocType", "type": "Link", "link_to": "Vehicle Job Order", "icon": "tool"},
    {"label": "Vehicle Inspections", "link_type": "DocType", "type": "Link", "link_to": "Vehicle Inspection", "icon": "check-circle"},
    {"label": "Vehicle Estimates", "link_type": "DocType", "type": "Link", "link_to": "Vehicle Estimate", "icon": "file-text"},
    {"label": "Vehicle Service Reminders", "link_type": "DocType", "type": "Link", "link_to": "Vehicle Service Reminder", "icon": "bell"},

    # Point of Sale & Billing Section
    {"label": "Point of Sale & Cashier", "type": "Section Break", "link_type": "DocType", "link_to": None, "icon": None},
    {"label": "Vehicle POS Invoices", "link_type": "DocType", "type": "Link", "link_to": "Vehicle POS Invoice", "icon": "file"},
    {"label": "POS Invoices", "link_type": "DocType", "type": "Link", "link_to": "POS Invoice", "icon": "credit-card"},
    {"label": "POS Opening Entry", "link_type": "DocType", "type": "Link", "link_to": "POS Opening Entry", "icon": "play"},
    {"label": "POS Closing Entry", "link_type": "DocType", "type": "Link", "link_to": "POS Closing Entry", "icon": "square"},
    {"label": "Cashier Profiles", "link_type": "DocType", "type": "Link", "link_to": "Cashier Profile", "icon": "user"},

    # Inventory & Parts Section
    {"label": "Inventory & Parts", "type": "Section Break", "link_type": "DocType", "link_to": None, "icon": None},
    {"label": "Items", "link_type": "DocType", "type": "Link", "link_to": "Item", "icon": "box"},
    {"label": "Stock Entries", "link_type": "DocType", "type": "Link", "link_to": "Stock Entry", "icon": "truck"},
    {"label": "Item Vehicle Compatibility", "link_type": "DocType", "type": "Link", "link_to": "Item Vehicle Compatibility", "icon": "check-square"},
    {"label": "Item Part Cross Reference", "link_type": "DocType", "type": "Link", "link_to": "Item Part Cross Reference", "icon": "git-commit"},
    {"label": "Bin Locations", "link_type": "DocType", "type": "Link", "link_to": "Bin Location", "icon": "archive"},
    {"label": "Warehouses", "link_type": "DocType", "type": "Link", "link_to": "Warehouse", "icon": "home"},

    # Vehicle Masters Section
    {"label": "Vehicle Masters", "type": "Section Break", "link_type": "DocType", "link_to": None, "icon": None},
    {"label": "Vehicle Makes", "link_type": "DocType", "type": "Link", "link_to": "Vehicle Make", "icon": "tag"},
    {"label": "Vehicle Models", "link_type": "DocType", "type": "Link", "link_to": "Vehicle Model", "icon": "list"},
    {"label": "Inspection Templates", "link_type": "DocType", "type": "Link", "link_to": "Inspection Template", "icon": "file-text"},

    # Analytical Reports Section
    {"label": "Analytical Reports", "type": "Section Break", "link_type": "DocType", "link_to": None, "icon": None},
    {"label": "Monthly Sales Report", "link_type": "Report", "type": "Link", "link_to": "Monthly Sales Report", "icon": "table"},
    {"label": "Detailed Sales Report", "link_type": "Report", "type": "Link", "link_to": "Detailed Sales Report", "icon": "table"},
    {"label": "Sales Analytics", "link_type": "Report", "type": "Link", "link_to": "Sales Analytics", "icon": "table"},
    {"label": "Sales Invoice Trends", "link_type": "Report", "type": "Link", "link_to": "Sales Invoice Trends", "icon": "table"},
    {"label": "POS Register", "link_type": "Report", "type": "Link", "link_to": "POS Register", "icon": "table"},
    {"label": "Daily Collection Report", "link_type": "Report", "type": "Link", "link_to": "Daily Collection Report", "icon": "table"},
    {"label": "Product Purchases", "link_type": "Report", "type": "Link", "link_to": "Product Purchases", "icon": "table"},
    {"label": "Purchase Order Report", "link_type": "Report", "type": "Link", "link_to": "Purchase Order Report", "icon": "table"},
    {"label": "Purchase Analytics", "link_type": "Report", "type": "Link", "link_to": "Purchase Analytics", "icon": "table"},
    {"label": "Top Suppliers", "link_type": "Report", "type": "Link", "link_to": "Top Suppliers", "icon": "table"},
    {"label": "Stock Balance", "link_type": "Report", "type": "Link", "link_to": "Stock Balance", "icon": "table"},
    {"label": "Warehouse Wise Stock Balance", "link_type": "Report", "type": "Link", "link_to": "Warehouse Wise Stock Balance", "icon": "table"},
    {"label": "Inventory Summary", "link_type": "Report", "type": "Link", "link_to": "Inventory Summary", "icon": "table"},
    {"label": "Monthly Job Orders", "link_type": "Report", "type": "Link", "link_to": "Monthly Job Orders", "icon": "table"},
    {"label": "Detailed Job Orders", "link_type": "Report", "type": "Link", "link_to": "Detailed Job Orders", "icon": "table"},
    {"label": "Top Vehicles Served", "link_type": "Report", "type": "Link", "link_to": "Top Vehicles Served", "icon": "table"},
    {"label": "Statement of Account", "link_type": "Report", "type": "Link", "link_to": "Statement of Account", "icon": "table"},
    {"label": "Check Register", "link_type": "Report", "type": "Link", "link_to": "Check Register", "icon": "table"},
    {"label": "Profit and Loss Statement", "link_type": "Report", "type": "Link", "link_to": "Profit and Loss Statement", "icon": "table"},
    {"label": "General Ledger", "link_type": "Report", "type": "Link", "link_to": "General Ledger", "icon": "table"}
]

# Ensure index, collapsible, etc. are set
for idx, it in enumerate(sidebar_items, 1):
    it["idx"] = idx
    it["collapsible"] = 1
    it["indent"] = 0
    it["keep_closed"] = 0
    it["show_arrow"] = 0
    it["child"] = 0 if it["type"] == "Section Break" else 1

sidebar_doc = {
    "title": "Vehicle Management",
    "module": "Vehicle Management",
    "header_icon": "car",
    "items": sidebar_items
}

req_sb = urllib.request.Request(
    f"{URL}/api/resource/Workspace%20Sidebar/Vehicle%20Management",
    data=urllib.parse.urlencode({'data': json.dumps(sidebar_doc)}).encode(),
    headers=H
)
req_sb.get_method = lambda: 'PUT'
res_sb = op.open(req_sb)
print(f"Workspace Sidebar 'Vehicle Management' updated! Status: {res_sb.status}")

# -------------------------------------------------------------
# 2. Fix Accounting Desktop Icon Link
# -------------------------------------------------------------
try:
    req_di = urllib.request.Request(
        f"{URL}/api/resource/Desktop%20Icon/Accounting",
        data=urllib.parse.urlencode({'data': json.dumps({"link_type": "Workspace Sidebar", "link_to": "Invoicing", "hidden": 0})}).encode(),
        headers=H
    )
    req_di.get_method = lambda: 'PUT'
    op.open(req_di)
    print("Desktop Icon 'Accounting' link_to updated to 'Invoicing'.")
except Exception as e:
    print("Accounting Desktop Icon update notice:", e)

# -------------------------------------------------------------
# 3. Update Vehicle Management Workspace (Full Analytical Dashboard, NO CARDS)
# -------------------------------------------------------------

# Number Cards
number_cards = [
    {"number_card_name": "Lifetime Total Revenue (PHP)", "label": "Lifetime Total Revenue (PHP)"},
    {"number_card_name": "Total Sales Amount", "label": "Total Sales Amount"},
    {"number_card_name": "Total Purchase Amount", "label": "Total Purchase Amount"},
    {"number_card_name": "Total Stock Value", "label": "Total Stock Value"},
    {"number_card_name": "Total Registered Vehicles", "label": "Total Registered Vehicles"},
    {"number_card_name": "Total Job Orders", "label": "Total Job Orders"},
    {"number_card_name": "Vehicle POS Invoices Count", "label": "Vehicle POS Invoices Count"}
]

# Charts
charts = [
    # Sales Analytics
    {"chart_name": "Vehicle POS Sales by Company", "label": "Vehicle POS Sales by Company"},
    {"chart_name": "Sales Order Trends", "label": "Sales Order Trends"},
    {"chart_name": "Item-wise Annual Sales", "label": "Item-wise Annual Sales"},
    {"chart_name": "Top Customers", "label": "Top Customers"},

    # Purchase Analytics
    {"chart_name": "Purchase Order Trends", "label": "Purchase Order Trends"},
    {"chart_name": "Top Suppliers", "label": "Top Suppliers"},
    {"chart_name": "Purchase Receipt Trends", "label": "Purchase Receipt Trends"},
    {"chart_name": "Incoming Bills (Purchase Invoice)", "label": "Incoming Bills (Purchase Invoice)"},

    # Inventory Analytics
    {"chart_name": "Warehouse wise Stock Value", "label": "Warehouse wise Stock Value"},
    {"chart_name": "Stock Value by Item Group", "label": "Stock Value by Item Group"},
    {"chart_name": "Item Shortage Summary", "label": "Item Shortage Summary"},
    {"chart_name": "Delivery Trends", "label": "Delivery Trends"},

    # Operations & Workshop Analytics
    {"chart_name": "VM Job Orders by Company", "label": "VM Job Orders by Company"},
    {"chart_name": "Vehicle Job Orders by Status", "label": "Vehicle Job Orders by Status"},
    {"chart_name": "Customer Vehicles by Make", "label": "Customer Vehicles by Make"},
    {"chart_name": "Job Card Analysis", "label": "Job Card Analysis"}
]

# Shortcuts (Launch Pills)
shortcuts = [
    {"label": "Vehicle POS Terminal", "type": "Page", "link_to": "vehicle_pos", "color": "Green"},
    {"label": "Vehicle Analytics Dashboard", "type": "Page", "link_to": "vehicle_analytics", "color": "Blue"},
    {"label": "Sales Analytics", "type": "Report", "link_to": "Sales Analytics", "color": "Orange", "is_query_report": 1},
    {"label": "Purchase Analytics", "type": "Report", "link_to": "Purchase Analytics", "color": "Purple", "is_query_report": 1},
    {"label": "Stock Balance", "type": "Report", "link_to": "Stock Balance", "color": "Green", "is_query_report": 1},
    {"label": "Warehouse Stock Balance", "type": "Report", "link_to": "Warehouse Wise Stock Balance", "color": "Cyan", "is_query_report": 1},
    {"label": "Profit and Loss Statement", "type": "Report", "link_to": "Profit and Loss Statement", "color": "Teal", "is_query_report": 1},
    {"label": "General Ledger", "type": "Report", "link_to": "General Ledger", "color": "Blue", "is_query_report": 1}
]

# EditorJS Content Blocks - 100% Analytical, NO module card breaks
content_blocks = [
    # Top KPI Metrics Header & Cards
    {
        "id": "hdr_kpi",
        "type": "header",
        "data": {
            "text": "<span class=\"h4\" style=\"color: #0fa76d;\"><b>📈 Executive KPI Overview</b></span>",
            "col": 12
        }
    },
    {"id": "nc_rev", "type": "number_card", "data": {"number_card_name": "Lifetime Total Revenue (PHP)", "col": 3}},
    {"id": "nc_sales", "type": "number_card", "data": {"number_card_name": "Total Sales Amount", "col": 3}},
    {"id": "nc_purch", "type": "number_card", "data": {"number_card_name": "Total Purchase Amount", "col": 3}},
    {"id": "nc_stock", "type": "number_card", "data": {"number_card_name": "Total Stock Value", "col": 3}},
    {"id": "nc_reg_veh", "type": "number_card", "data": {"number_card_name": "Total Registered Vehicles", "col": 4}},
    {"id": "nc_jobs", "type": "number_card", "data": {"number_card_name": "Total Job Orders", "col": 4}},
    {"id": "nc_vpos", "type": "number_card", "data": {"number_card_name": "Vehicle POS Invoices Count", "col": 4}},

    # Quick Analytical Shortcuts Header & Pills
    {
        "id": "hdr_shortcuts",
        "type": "header",
        "data": {
            "text": "<span class=\"h4\" style=\"color: #2b6cb0;\"><b>🚀 Quick Analytical Launchers &amp; Reports</b></span>",
            "col": 12
        }
    },
    {"id": "sc_vpos_term", "type": "shortcut", "data": {"shortcut_name": "Vehicle POS Terminal", "col": 3}},
    {"id": "sc_analytics_dash", "type": "shortcut", "data": {"shortcut_name": "Vehicle Analytics Dashboard", "col": 3}},
    {"id": "sc_sales_an", "type": "shortcut", "data": {"shortcut_name": "Sales Analytics", "col": 3}},
    {"id": "sc_purch_an", "type": "shortcut", "data": {"shortcut_name": "Purchase Analytics", "col": 3}},
    {"id": "sc_stock_bal", "type": "shortcut", "data": {"shortcut_name": "Stock Balance", "col": 3}},
    {"id": "sc_wh_bal", "type": "shortcut", "data": {"shortcut_name": "Warehouse Stock Balance", "col": 3}},
    {"id": "sc_pnl", "type": "shortcut", "data": {"shortcut_name": "Profit and Loss Statement", "col": 3}},
    {"id": "sc_gl", "type": "shortcut", "data": {"shortcut_name": "General Ledger", "col": 3}},

    # Section 1: Sales & Revenue Analytics
    {
        "id": "hdr_sales_analytics",
        "type": "header",
        "data": {
            "text": "<span class=\"h4\" style=\"color: #319795;\"><b>💰 Sales &amp; Revenue Analytics</b></span>",
            "col": 12
        }
    },
    {"id": "ch_vpos_sales", "type": "chart", "data": {"chart_name": "Vehicle POS Sales by Company", "col": 6}},
    {"id": "ch_sales_trends", "type": "chart", "data": {"chart_name": "Sales Order Trends", "col": 6}},
    {"id": "ch_item_sales", "type": "chart", "data": {"chart_name": "Item-wise Annual Sales", "col": 6}},
    {"id": "ch_top_cust", "type": "chart", "data": {"chart_name": "Top Customers", "col": 6}},

    # Section 2: Purchase & Vendor Analytics
    {
        "id": "hdr_purch_analytics",
        "type": "header",
        "data": {
            "text": "<span class=\"h4\" style=\"color: #805ad5;\"><b>🛒 Purchase &amp; Vendor Analytics</b></span>",
            "col": 12
        }
    },
    {"id": "ch_po_trends", "type": "chart", "data": {"chart_name": "Purchase Order Trends", "col": 6}},
    {"id": "ch_top_supp", "type": "chart", "data": {"chart_name": "Top Suppliers", "col": 6}},
    {"id": "ch_pr_trends", "type": "chart", "data": {"chart_name": "Purchase Receipt Trends", "col": 6}},
    {"id": "ch_in_bills", "type": "chart", "data": {"chart_name": "Incoming Bills (Purchase Invoice)", "col": 6}},

    # Section 3: Inventory & Warehouse Analytics
    {
        "id": "hdr_inv_analytics",
        "type": "header",
        "data": {
            "text": "<span class=\"h4\" style=\"color: #d69e2e;\"><b>📦 Inventory &amp; Stock Analytics</b></span>",
            "col": 12
        }
    },
    {"id": "ch_wh_stock", "type": "chart", "data": {"chart_name": "Warehouse wise Stock Value", "col": 6}},
    {"id": "ch_grp_stock", "type": "chart", "data": {"chart_name": "Stock Value by Item Group", "col": 6}},
    {"id": "ch_item_shortage", "type": "chart", "data": {"chart_name": "Item Shortage Summary", "col": 6}},
    {"id": "ch_del_trends", "type": "chart", "data": {"chart_name": "Delivery Trends", "col": 6}},

    # Section 4: Vehicle & Workshop Operations Analytics
    {
        "id": "hdr_ops_analytics",
        "type": "header",
        "data": {
            "text": "<span class=\"h4\" style=\"color: #e53e3e;\"><b>🔧 Workshop &amp; Fleet Operations Analytics</b></span>",
            "col": 12
        }
    },
    {"id": "ch_jo_co", "type": "chart", "data": {"chart_name": "VM Job Orders by Company", "col": 6}},
    {"id": "ch_jo_status", "type": "chart", "data": {"chart_name": "Vehicle Job Orders by Status", "col": 6}},
    {"id": "ch_veh_makes", "type": "chart", "data": {"chart_name": "Customer Vehicles by Make", "col": 6}},
    {"id": "ch_job_card", "type": "chart", "data": {"chart_name": "Job Card Analysis", "col": 6}}
]

workspace_doc = {
    "title": "Vehicle Management",
    "public": 1,
    "module": "Vehicle Management",
    "icon": "car",
    "indicator_color": "blue",
    "number_cards": number_cards,
    "charts": charts,
    "shortcuts": shortcuts,
    "links": [],  # NO module link cards!
    "content": json.dumps(content_blocks)
}

req_ws = urllib.request.Request(
    f"{URL}/api/resource/Workspace/Vehicle%20Management",
    data=urllib.parse.urlencode({'data': json.dumps(workspace_doc)}).encode(),
    headers=H
)
req_ws.get_method = lambda: 'PUT'
res_ws = op.open(req_ws)
print(f"Workspace 'Vehicle Management' updated! Status: {res_ws.status}")

# -------------------------------------------------------------
# 4. Clear Cache & Commit on Server
# -------------------------------------------------------------
try:
    op.open(urllib.request.Request(f"{URL}/api/method/frappe.desk.doctype.workspace.workspace.clear_workspace_cache", headers=H))
    print("Cleared workspace cache.")
except Exception as e:
    print("Cache clear note:", e)

print("\n=== DEPLOYMENT COMPLETE SUCCESSFULLY ===")
