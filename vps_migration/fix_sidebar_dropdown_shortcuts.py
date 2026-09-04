import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

# 1. Update Navbar Settings
res = op.open(urllib.request.Request(f"{URL}/api/resource/Navbar%20Settings/Navbar%20Settings", headers=H))
ns = json.loads(res.read().decode()).get('data', {})

settings_items = [
    {
        "item_label": "🚗 Vehicle Management Workspace",
        "item_type": "Route",
        "route": "/desk#workspace/Vehicle%20Management",
        "hidden": 0,
        "is_standard": 0
    },
    {
        "item_label": "🐴 Vehicle POS Terminal",
        "item_type": "Route",
        "route": "/pos-terminal",
        "hidden": 0,
        "is_standard": 0
    },
    {
        "item_label": "📊 Executive Dashboard",
        "item_type": "Route",
        "route": "/executive-dashboard",
        "hidden": 0,
        "is_standard": 0
    }
]

ns['settings_dropdown'] = settings_items

put_req = urllib.request.Request(
    f"{URL}/api/resource/Navbar%20Settings/Navbar%20Settings",
    data=urllib.parse.urlencode({'data': json.dumps(ns)}).encode(),
    headers=H
)
put_req.get_method = lambda: 'PUT'
op.open(put_req)
print("Updated Navbar Settings dropdown items!")

# 2. Update Client Script: VM Header Shortcut Button with bulletproof click handlers
client_script_content = """
(function() {
  const VM_SIDEBAR_ITEMS = [
    { label: "Vehicle Management", link_to: "Vehicle Management", link_type: "Workspace", type: "Link", icon: "home", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle POS Terminal", link_to: "vehicle_pos", link_type: "Page", type: "Link", icon: "panel-top", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Analytics", link_to: "vehicle_analytics", link_type: "Page", type: "Link", icon: "bar-chart", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Operations & Workshop", type: "Section Break", link_type: "DocType", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Customer Vehicles", link_to: "Customer Vehicle", link_type: "DocType", type: "Link", icon: "car", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Job Orders", link_to: "Vehicle Job Order", link_type: "DocType", type: "Link", icon: "tool", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Inspections", link_to: "Vehicle Inspection", link_type: "DocType", type: "Link", icon: "check-circle", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Estimates", link_to: "Vehicle Estimate", link_type: "DocType", type: "Link", icon: "file-text", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Service Reminders", link_to: "Vehicle Service Reminder", link_type: "DocType", type: "Link", icon: "bell", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Point of Sale & Cashier", type: "Section Break", link_type: "DocType", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle POS Invoices", link_to: "Vehicle POS Invoice", link_type: "DocType", type: "Link", icon: "file", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "POS Invoices", link_to: "POS Invoice", link_type: "DocType", type: "Link", icon: "credit-card", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "POS Opening Entry", link_to: "POS Opening Entry", link_type: "DocType", type: "Link", icon: "play", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "POS Closing Entry", link_to: "POS Closing Entry", link_type: "DocType", type: "Link", icon: "square", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Cashier Profiles", link_to: "Cashier Profile", link_type: "DocType", type: "Link", icon: "user", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Inventory & Parts", type: "Section Break", link_type: "DocType", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Items", link_to: "Item", link_type: "DocType", type: "Link", icon: "box", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Stock Entries", link_to: "Stock Entry", link_type: "DocType", type: "Link", icon: "truck", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Item Vehicle Compatibility", link_to: "Item Vehicle Compatibility", link_type: "DocType", type: "Link", icon: "check-square", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Item Part Cross Reference", link_to: "Item Part Cross Reference", link_type: "DocType", type: "Link", icon: "git-commit", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Bin Locations", link_to: "Bin Location", link_type: "DocType", type: "Link", icon: "archive", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Warehouses", link_to: "Warehouse", link_type: "DocType", type: "Link", icon: "home", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Masters", type: "Section Break", link_type: "DocType", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Makes", link_to: "Vehicle Make", link_type: "DocType", type: "Link", icon: "tag", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Models", link_to: "Vehicle Model", link_type: "DocType", type: "Link", icon: "list", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Inspection Templates", link_to: "Inspection Template", link_type: "DocType", type: "Link", icon: "file-text", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Analytical Reports", type: "Section Break", link_type: "DocType", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Monthly Sales Report", link_to: "Monthly Sales Report", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Sales Invoice" } },
    { label: "Detailed Sales Report", link_to: "Detailed Sales Report", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Sales Invoice" } },
    { label: "Sales Analytics", link_to: "Sales Analytics", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Sales Invoice" } },
    { label: "Sales Invoice Trends", link_to: "Sales Invoice Trends", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Sales Invoice" } },
    { label: "POS Register", link_to: "POS Register", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "POS Invoice" } },
    { label: "Daily Collection Report", link_to: "Daily Collection Report", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "POS Invoice" } },
    { label: "Product Purchases", link_to: "Product Purchases", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Purchase Invoice" } },
    { label: "Purchase Order Report", link_to: "Purchase Order Report", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Purchase Order" } },
    { label: "Purchase Analytics", link_to: "Purchase Analytics", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Purchase Order" } },
    { label: "Top Suppliers", link_to: "Top Suppliers", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Purchase Order" } },
    { label: "Stock Balance", link_to: "Stock Balance", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Stock Ledger Entry" } },
    { label: "Warehouse Wise Stock Balance", link_to: "Warehouse Wise Stock Balance", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Stock Ledger Entry" } },
    { label: "Inventory Summary", link_to: "Inventory Summary", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Stock Ledger Entry" } },
    { label: "Monthly Job Orders", link_to: "Monthly Job Orders", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Vehicle Job Order" } },
    { label: "Detailed Job Orders", link_to: "Detailed Job Orders", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Vehicle Job Order" } },
    { label: "Top Vehicles Served", link_to: "Top Vehicles Served", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Vehicle Job Order" } },
    { label: "Statement of Account", link_to: "Statement of Account", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Customer" } },
    { label: "Check Register", link_to: "Check Register", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Payment Entry" } },
    { label: "Profit and Loss Statement", link_to: "Profit and Loss Statement", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "GL Entry" } },
    { label: "General Ledger", link_to: "General Ledger", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "GL Entry" } }
  ];

  function ensureVMBootSidebar() {
    if (window.frappe && frappe.boot) {
      if (!frappe.boot.workspace_sidebar_item) {
        frappe.boot.workspace_sidebar_item = {};
      }
      frappe.boot.workspace_sidebar_item["vehicle management"] = VM_SIDEBAR_ITEMS;
      frappe.boot.workspace_sidebar_item["Vehicle Management"] = VM_SIDEBAR_ITEMS;
    }
  }

  function injectVMHeader() {
    ensureVMBootSidebar();
    if ($("#navbar-vm-shortcut").length) return;
    const userArea = $(".navbar-nav .dropdown-notifications, .navbar-nav .dropdown-help, .navbar-nav .dropdown-user").first();
    if (!userArea.length) return;

    const style = `
      <style id="vm-header-shortcut-styles">
        .vm-header-pill {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
          color: #ffffff !important;
          border: none !important;
          border-radius: 20px !important;
          padding: 4px 12px !important;
          font-weight: 800 !important;
          font-size: 12px !important;
          display: inline-flex !important;
          align-items: center !important;
          box-shadow: 0 2px 6px rgba(16, 185, 129, 0.35) !important;
          transition: all 0.2s ease !important;
          cursor: pointer !important;
          margin-right: 8px !important;
        }
        .vm-header-pill:hover {
          background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
          color: #ffffff !important;
          text-decoration: none !important;
          transform: translateY(-1px) !important;
        }
        .vm-dropdown-menu {
          border-radius: 14px !important;
          border: 1px solid #e2e8f0 !important;
          padding: 8px !important;
          min-width: 260px !important;
          box-shadow: 0 20px 25px -5px rgba(0,0,0,0.15) !important;
          margin-top: 6px !important;
        }
        .vm-dropdown-menu .dropdown-item {
          border-radius: 8px !important;
          padding: 8px 12px !important;
          font-size: 13px !important;
          font-weight: 600 !important;
          cursor: pointer !important;
        }
        .vm-dropdown-menu .dropdown-item:hover {
          background: #f0fdf4 !important;
          color: #0fa76d !important;
        }
      </style>
    `;
    if (!$("#vm-header-shortcut-styles").length) {
      $("head").append(style);
    }

    const vmHtml = `
      <li class="nav-item dropdown d-flex align-items-center mr-2" id="navbar-vm-shortcut">
        <a class="nav-link dropdown-toggle btn btn-sm vm-header-pill" href="/desk#workspace/Vehicle%20Management" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" title="Vehicle Management Workspace">
          <span style="font-size: 14px; margin-right: 4px;">🚗</span>
          <span style="font-weight: 900; font-size: 13px; letter-spacing: 0.5px;">VM</span>
        </a>
        <div class="dropdown-menu dropdown-menu-right vm-dropdown-menu shadow-lg">
          <div class="dropdown-header text-uppercase font-weight-bold" style="color: #0fa76d; letter-spacing: 0.5px; font-size: 11px;">
            🚗 Vehicle Management
          </div>
          <a class="dropdown-item d-flex align-items-center" href="/desk#workspace/Vehicle%20Management">
            <span class="mr-2" style="font-size: 16px;">📂</span>
            <div>
              <div class="font-weight-bold" style="color: #0c1a18;">Vehicle Workspace</div>
              <small class="text-muted">Operations &amp; analytics command center</small>
            </div>
          </a>
          <a class="dropdown-item d-flex align-items-center" href="/pos-terminal">
            <span class="mr-2" style="font-size: 16px;">🐴</span>
            <div>
              <div class="font-weight-bold" style="color: #0c1a18;">Vehicle POS Terminal</div>
              <small class="text-muted">Cashier register &amp; receipts</small>
            </div>
          </a>
          <div class="dropdown-divider"></div>
          <a class="dropdown-item d-flex align-items-center justify-content-between" href="/executive-dashboard" target="_blank">
            <div class="d-flex align-items-center">
              <span class="mr-2">📊</span>
              <span class="font-weight-bold" style="color: #0c1a18;">Executive Dashboard</span>
            </div>
            <span class="badge badge-success ml-2" style="background: #16c784; color: #04201a; font-weight: 800;">LIVE</span>
          </a>
        </div>
      </li>
    `;

    userArea.before(vmHtml);
  }

  // Handle all dropdown clicks globally and reliably
  $(document).on("click", ".sidebar-header-menu .dropdown-menu-item, .dropdown-menu-item", function(e) {
    const text = $(this).text().trim();
    if (text.includes("Vehicle Management Workspace") || text.includes("Vehicle Workspace")) {
      e.preventDefault();
      e.stopPropagation();
      window.location.href = "/desk#workspace/Vehicle%20Management";
    } else if (text.includes("Vehicle POS Terminal")) {
      e.preventDefault();
      e.stopPropagation();
      window.location.href = "/pos-terminal";
    } else if (text.includes("Executive Dashboard")) {
      e.preventDefault();
      e.stopPropagation();
      window.open("/executive-dashboard", "_blank");
    }
  });

  ensureVMBootSidebar();
  $(document).ready(function() {
    injectVMHeader();
    setTimeout(injectVMHeader, 200);
    setTimeout(injectVMHeader, 1000);
    setTimeout(injectVMHeader, 2500);
  });
  $(document).on("toolbar_setup page-change", injectVMHeader);
})();
"""

# Update Client Script in DB
res_cs = op.open(urllib.request.Request(f"{URL}/api/resource/Client%20Script/VM%20Header%20Shortcut%20Button", headers=H))
cs_doc = json.loads(res_cs.read().decode()).get('data', {})
cs_doc['script'] = client_script_content
put_cs = urllib.request.Request(
    f"{URL}/api/resource/Client%20Script/VM%20Header%20Shortcut%20Button",
    data=urllib.parse.urlencode({'data': json.dumps(cs_doc)}).encode(),
    headers=H
)
put_cs.get_method = lambda: 'PUT'
op.open(put_cs)
print("Updated Client Script 'VM Header Shortcut Button' in DB!")
