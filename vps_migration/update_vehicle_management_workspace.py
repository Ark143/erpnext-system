import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

# Define Charts
charts = [
    {"chart_name": "VM Job Orders by Company", "label": "Job Orders by Branch"},
    {"chart_name": "Vehicle POS Sales by Company", "label": "POS Sales by Branch"},
    {"chart_name": "Customer Vehicles by Make", "label": "Customer Vehicles by Make"},
    {"chart_name": "Vehicle Job Orders by Status", "label": "Job Orders by Status"}
]

# Define Shortcuts
shortcuts = [
    {"label": "Vehicle Analytics Dashboard", "type": "Page", "link_to": "vehicle_analytics", "color": "Blue"},
    {"label": "Vehicle POS Terminal", "type": "Page", "link_to": "vehicle_pos", "color": "Green"},
    {"label": "Customer Vehicles", "type": "DocType", "link_to": "Customer Vehicle", "doc_view": "List", "color": "Blue"},
    {"label": "Vehicle Job Orders", "type": "DocType", "link_to": "Vehicle Job Order", "doc_view": "List", "color": "Orange"},
    {"label": "Vehicle Inspections", "type": "DocType", "link_to": "Vehicle Inspection", "doc_view": "List", "color": "Purple"},
    {"label": "Vehicle POS Invoices", "type": "DocType", "link_to": "Vehicle POS Invoice", "doc_view": "List", "color": "Red"},
    {"label": "POS Invoices", "type": "DocType", "link_to": "POS Invoice", "doc_view": "List", "color": "Yellow"},
    {"label": "Vehicle Estimates", "type": "DocType", "link_to": "Vehicle Estimate", "doc_view": "List", "color": "Grey"},
    {"label": "Bin Locations", "type": "DocType", "link_to": "Bin Location", "doc_view": "List", "color": "Green"}
]

# Define Links
links = [
    # Card 1: Operations & Front Desk
    {"type": "Card Break", "label": "Operations & Front Desk", "icon": "tool", "description": "Workshop counter & job execution", "link_count": 8},
    {"type": "Link", "label": "Vehicle POS Terminal", "link_type": "Page", "link_to": "vehicle_pos"},
    {"type": "Link", "label": "Vehicle POS Invoice", "link_type": "DocType", "link_to": "Vehicle POS Invoice"},
    {"type": "Link", "label": "Vehicle Job Order", "link_type": "DocType", "link_to": "Vehicle Job Order"},
    {"type": "Link", "label": "Vehicle Inspection", "link_type": "DocType", "link_to": "Vehicle Inspection"},
    {"type": "Link", "label": "Vehicle Estimate", "link_type": "DocType", "link_to": "Vehicle Estimate"},
    {"type": "Link", "label": "POS Invoice", "link_type": "DocType", "link_to": "POS Invoice"},
    {"type": "Link", "label": "POS Opening Entry", "link_type": "DocType", "link_to": "POS Opening Entry"},
    {"type": "Link", "label": "POS Closing Entry", "link_type": "DocType", "link_to": "POS Closing Entry"},

    # Card 2: Vehicle Masters & Registry
    {"type": "Card Break", "label": "Vehicle Masters & Registry", "icon": "truck", "description": "Vehicles, customers & vehicle profiles", "link_count": 7},
    {"type": "Link", "label": "Customer Vehicle", "link_type": "DocType", "link_to": "Customer Vehicle"},
    {"type": "Link", "label": "Customer", "link_type": "DocType", "link_to": "Customer"},
    {"type": "Link", "label": "Vehicle Make", "link_type": "DocType", "link_to": "Vehicle Make"},
    {"type": "Link", "label": "Vehicle Model", "link_type": "DocType", "link_to": "Vehicle Model"},
    {"type": "Link", "label": "Vehicle Insurance", "link_type": "DocType", "link_to": "Vehicle Insurance"},
    {"type": "Link", "label": "Vehicle Warranty", "link_type": "DocType", "link_to": "Vehicle Warranty"},
    {"type": "Link", "label": "Bin Location", "link_type": "DocType", "link_to": "Bin Location"},

    # Card 3: Reports & Analytics
    {"type": "Card Break", "label": "Reports & Analytics", "icon": "bar-chart", "description": "Management dashboards & logs", "link_count": 5},
    {"type": "Link", "label": "Vehicle Analytics Dashboard", "link_type": "Page", "link_to": "vehicle_analytics"},
    {"type": "Link", "label": "POS Register", "link_type": "Report", "link_to": "POS Register", "is_query_report": 1},
    {"type": "Link", "label": "Sales Invoice Trends", "link_type": "Report", "link_to": "Sales Invoice Trends", "is_query_report": 1},
    {"type": "Link", "label": "Job Card Summary", "link_type": "Report", "link_to": "Job Card Summary", "is_query_report": 1},
    {"type": "Link", "label": "Mechanic Jobs", "link_type": "Report", "link_to": "Mechanic Jobs", "is_query_report": 1},

    # Card 4: Inventory & Service Parts
    {"type": "Card Break", "label": "Inventory & Service Parts", "icon": "box", "description": "Parts, lubricants, tires & stock movements", "link_count": 5},
    {"type": "Link", "label": "Item", "link_type": "DocType", "link_to": "Item"},
    {"type": "Link", "label": "Stock Entry", "link_type": "DocType", "link_to": "Stock Entry"},
    {"type": "Link", "label": "Stock Balance", "link_type": "Report", "link_to": "Stock Balance", "is_query_report": 1},
    {"type": "Link", "label": "Warehouse Wise Stock Balance", "link_type": "Report", "link_to": "Warehouse Wise Stock Balance", "is_query_report": 1},
    {"type": "Link", "label": "Warehouse", "link_type": "DocType", "link_to": "Warehouse"}
]

# Define Content (EditorJS layout)
content = [
    {
        "id": "header_analytics",
        "type": "header",
        "data": {
            "text": "<span class=\"h4\"><b>Vehicle Management Analytics &amp; KPIs</b></span>",
            "col": 12
        }
    },
    {
        "id": "nc_reg_vehicles",
        "type": "number_card",
        "data": {
            "number_card_name": "Total Registered Vehicles",
            "col": 3
        }
    },
    {
        "id": "nc_job_orders",
        "type": "number_card",
        "data": {
            "number_card_name": "Total Job Orders",
            "col": 3
        }
    },
    {
        "id": "nc_vpos_invoices",
        "type": "number_card",
        "data": {
            "number_card_name": "Vehicle POS Invoices Count",
            "col": 3
        }
    },
    {
        "id": "nc_revenue",
        "type": "number_card",
        "data": {
            "number_card_name": "Lifetime Total Revenue (PHP)",
            "col": 3
        }
    },
    {
        "id": "chart_job_orders",
        "type": "chart",
        "data": {
            "chart_name": "VM Job Orders by Company",
            "col": 6
        }
    },
    {
        "id": "chart_vpos_sales",
        "type": "chart",
        "data": {
            "chart_name": "Vehicle POS Sales by Company",
            "col": 6
        }
    },
    {
        "id": "chart_makes",
        "type": "chart",
        "data": {
            "chart_name": "Customer Vehicles by Make",
            "col": 6
        }
    },
    {
        "id": "chart_status",
        "type": "chart",
        "data": {
            "chart_name": "Vehicle Job Orders by Status",
            "col": 6
        }
    },
    {
        "id": "header_shortcuts",
        "type": "header",
        "data": {
            "text": "<span class=\"h4\"><b>Quick Shortcuts &amp; Actions</b></span>",
            "col": 12
        }
    },
    {
        "id": "sc_analytics",
        "type": "shortcut",
        "data": {
            "shortcut_name": "Vehicle Analytics Dashboard",
            "col": 3
        }
    },
    {
        "id": "sc_vpos",
        "type": "shortcut",
        "data": {
            "shortcut_name": "Vehicle POS Terminal",
            "col": 3
        }
    },
    {
        "id": "sc_cust_veh",
        "type": "shortcut",
        "data": {
            "shortcut_name": "Customer Vehicles",
            "col": 3
        }
    },
    {
        "id": "sc_job_orders",
        "type": "shortcut",
        "data": {
            "shortcut_name": "Vehicle Job Orders",
            "col": 3
        }
    },
    {
        "id": "sc_inspections",
        "type": "shortcut",
        "data": {
            "shortcut_name": "Vehicle Inspections",
            "col": 3
        }
    },
    {
        "id": "sc_vpos_inv",
        "type": "shortcut",
        "data": {
            "shortcut_name": "Vehicle POS Invoices",
            "col": 3
        }
    },
    {
        "id": "sc_pos_inv",
        "type": "shortcut",
        "data": {
            "shortcut_name": "POS Invoices",
            "col": 3
        }
    },
    {
        "id": "sc_bins",
        "type": "shortcut",
        "data": {
            "shortcut_name": "Bin Locations",
            "col": 3
        }
    },
    {
        "id": "header_modules",
        "type": "header",
        "data": {
            "text": "<span class=\"h4\"><b>Vehicle Management Modules &amp; Reports</b></span>",
            "col": 12
        }
    },
    {
        "id": "card_ops",
        "type": "card",
        "data": {
            "card_name": "Operations & Front Desk",
            "col": 4
        }
    },
    {
        "id": "card_masters",
        "type": "card",
        "data": {
            "card_name": "Vehicle Masters & Registry",
            "col": 4
        }
    },
    {
        "id": "card_reports",
        "type": "card",
        "data": {
            "card_name": "Reports & Analytics",
            "col": 4
        }
    },
    {
        "id": "card_inventory",
        "type": "card",
        "data": {
            "card_name": "Inventory & Service Parts",
            "col": 4
        }
    }
]

# Update the Workspace document
ws_update = {
    "title": "Vehicle Management",
    "public": 1,
    "module": "Vehicle Management",
    "charts": charts,
    "shortcuts": shortcuts,
    "links": links,
    "content": json.dumps(content)
}

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Workspace/Vehicle%20Management',
    data=urllib.parse.urlencode({'data': json.dumps(ws_update)}).encode(),
    headers=H
)
req.get_method = lambda: 'PUT'
res = op.open(req)
print("Workspace 'Vehicle Management' updated successfully!")
print("Response status:", res.status)
