import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

js_snippet = """
(function() {
  const VM_SIDEBAR_ITEMS = [
    // Top Links
    { label: "Vehicle Management", link_to: "Vehicle Management", link_type: "Workspace", type: "Link", icon: "home", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle POS Terminal", link_to: "vehicle_pos", link_type: "Page", type: "Link", icon: "panel-top", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Analytics", link_to: "vehicle_analytics", link_type: "Page", type: "Link", icon: "bar-chart", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },

    // Operations & Workshop
    { label: "Operations & Workshop", type: "Section Break", link_type: "DocType", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Customer Vehicles", link_to: "Customer Vehicle", link_type: "DocType", type: "Link", icon: "car", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Job Orders", link_to: "Vehicle Job Order", link_type: "DocType", type: "Link", icon: "tool", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Inspections", link_to: "Vehicle Inspection", link_type: "DocType", type: "Link", icon: "check-circle", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Estimates", link_to: "Vehicle Estimate", link_type: "DocType", type: "Link", icon: "file-text", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Service Reminders", link_to: "Vehicle Service Reminder", link_type: "DocType", type: "Link", icon: "bell", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },

    // Point of Sale & Billing
    { label: "Point of Sale & Cashier", type: "Section Break", link_type: "DocType", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle POS Invoices", link_to: "Vehicle POS Invoice", link_type: "DocType", type: "Link", icon: "file", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "POS Invoices", link_to: "POS Invoice", link_type: "DocType", type: "Link", icon: "credit-card", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "POS Opening Entry", link_to: "POS Opening Entry", link_type: "DocType", type: "Link", icon: "play", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "POS Closing Entry", link_to: "POS Closing Entry", link_type: "DocType", type: "Link", icon: "square", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Cashier Profiles", link_to: "Cashier Profile", link_type: "DocType", type: "Link", icon: "user", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },

    // Inventory & Parts
    { label: "Inventory & Parts", type: "Section Break", link_type: "DocType", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Items", link_to: "Item", link_type: "DocType", type: "Link", icon: "box", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Stock Entries", link_to: "Stock Entry", link_type: "DocType", type: "Link", icon: "truck", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Item Vehicle Compatibility", link_to: "Item Vehicle Compatibility", link_type: "DocType", type: "Link", icon: "check-square", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Item Part Cross Reference", link_to: "Item Part Cross Reference", link_type: "DocType", type: "Link", icon: "git-commit", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Bin Locations", link_to: "Bin Location", link_type: "DocType", type: "Link", icon: "archive", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Warehouses", link_to: "Warehouse", link_type: "DocType", type: "Link", icon: "home", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },

    // Vehicle Masters
    { label: "Vehicle Masters", type: "Section Break", link_type: "DocType", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Makes", link_to: "Vehicle Make", link_type: "DocType", type: "Link", icon: "tag", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Models", link_to: "Vehicle Model", link_type: "DocType", type: "Link", icon: "list", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Inspection Templates", link_to: "Inspection Template", link_type: "DocType", type: "Link", icon: "file-text", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },

    // Analytical Reports
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
    if (window.frappe && frappe.boot && frappe.boot.workspace_sidebar_item) {
      frappe.boot.workspace_sidebar_item['vehicle management'] = {
        label: "Vehicle Management",
        header_icon: "car",
        module: "Vehicle Management",
        items: VM_SIDEBAR_ITEMS
      };
    }
  }

  function injectVMHeader() {
    ensureVMBootSidebar();
    if ($("#navbar-vm-shortcut").length > 0) return;
    const userArea = $("#toolbar-user") || $(".dropdown-user") || $(".navbar-nav:last");
    if (!userArea.length) return;

    const style = `
      <style id="vm-header-shortcut-styles">
        .vm-header-pill {
          background: #16c784 !important;
          color: #04201a !important;
          font-weight: 900 !important;
          border-radius: 8px !important;
          padding: 4px 10px !important;
          height: 30px !important;
          display: inline-flex !important;
          align-items: center !important;
          box-shadow: 0 2px 5px rgba(22, 199, 132, 0.35) !important;
          border: 1px solid rgba(4, 32, 26, 0.1) !important;
          transition: all 0.15s ease !important;
          cursor: pointer !important;
          margin-right: 6px !important;
        }
        .vm-header-pill:hover, .vm-header-pill:focus {
          background: #0fa76d !important;
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
              <div class="font-weight-bold" style="color: #0c1a18;">Vehicle Workspace (Analytical Dashboard)</div>
              <small class="text-muted">Sales, purchase, stock &amp; operations analytics</small>
            </div>
          </a>
          <a class="dropdown-item d-flex align-items-center" href="/desk/vehicle_pos">
            <span class="mr-2" style="font-size: 16px;">🐴</span>
            <div>
              <div class="font-weight-bold" style="color: #0c1a18;">Vehicle POS Terminal</div>
              <small class="text-muted">Cashier register &amp; receipts</small>
            </div>
          </a>
          <div class="dropdown-divider"></div>
          <div class="dropdown-header text-uppercase font-weight-bold" style="color: #5b6b68; letter-spacing: 0.5px; font-size: 11px;">
            📋 Quick Shortcuts
          </div>
          <a class="dropdown-item d-flex align-items-center" href="/desk#List/Customer%20Vehicle">
            <span class="mr-2">🚘</span> <span>Customer Vehicles</span>
          </a>
          <a class="dropdown-item d-flex align-items-center" href="/desk#List/Vehicle%20Inspection">
            <span class="mr-2">🔍</span> <span>Vehicle Inspections</span>
          </a>
          <a class="dropdown-item d-flex align-items-center" href="/desk#List/Vehicle%20Job%20Order">
            <span class="mr-2">🔧</span> <span>Workshop Job Orders</span>
          </a>
          <a class="dropdown-item d-flex align-items-center" href="/desk#List/Vehicle%20Estimate">
            <span class="mr-2">📝</span> <span>Estimates &amp; Quotations</span>
          </a>
          <a class="dropdown-item d-flex align-items-center" href="/desk#List/Vehicle%20Service%20Reminder">
            <span class="mr-2">⏰</span> <span>Service Reminders</span>
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

script_doc = {
    'doctype': 'Client Script',
    'name': 'VM Header Shortcut Button',
    'dt': 'Workspace',
    'view': 'List',
    'enabled': 1,
    'script': js_snippet
}

H = {'Content-Type': 'application/json', 'Accept': 'application/json'}

try:
    req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Client%20Script/VM%20Header%20Shortcut%20Button', data=json.dumps(script_doc).encode(), headers=H, method='PUT')
    res = opener.open(req)
    print("Updated Client Script: HTTP", res.status)
except:
    req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Client%20Script', data=json.dumps(script_doc).encode(), headers=H, method='POST')
    res = opener.open(req)
    print("Created Client Script: HTTP", res.status)
