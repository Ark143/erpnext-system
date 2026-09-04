import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

# 1. Update Server Script: VM Safe Open Count API
server_script_code = """
doctype = frappe.form_dict.get('doctype')
name = frappe.form_dict.get('name')
items_raw = frappe.form_dict.get('items')

if isinstance(items_raw, str):
    try:
        import json
        items = json.loads(items_raw)
    except Exception:
        items = []
elif isinstance(items_raw, list):
    items = items_raw
else:
    items = []

internal_links_found = []
external_links_found = []

if doctype and name and frappe.db.exists(doctype, name):
    doc = frappe.get_doc(doctype, name)
    
    if doctype == 'Vehicle Job Order':
        # Internal links (on doc itself)
        if doc.get('customer'):
            internal_links_found.append({
                'doctype': 'Customer',
                'count': 1,
                'open_count': 0,
                'names': [doc.get('customer')]
            })
        if doc.get('vehicle'):
            internal_links_found.append({
                'doctype': 'Customer Vehicle',
                'count': 1,
                'open_count': 0,
                'names': [doc.get('vehicle')]
            })
        if doc.get('estimate'):
            internal_links_found.append({
                'doctype': 'Vehicle Estimate',
                'count': 1,
                'open_count': 0,
                'names': [doc.get('estimate')]
            })
            
        # External linked transactions (referencing this JO)
        for dt, fld in [
            ('Sales Invoice', 'custom_vehicle_job_order'),
            ('Sales Order', 'custom_vehicle_job_order'),
            ('Quotation', 'custom_vehicle_job_order'),
            ('Vehicle Inspection', 'job_order')
        ]:
            if not items or dt in items:
                cnt = 0
                try:
                    meta = frappe.get_meta(dt)
                    if meta.has_field(fld):
                        cnt = len(frappe.get_all(dt, filters={fld: name}, limit=100))
                except Exception:
                    cnt = 0
                external_links_found.append({
                    'doctype': dt,
                    'count': cnt,
                    'open_count': 0
                })

    elif doctype == 'Vehicle Estimate':
        if doc.get('customer'):
            internal_links_found.append({
                'doctype': 'Customer',
                'count': 1,
                'open_count': 0,
                'names': [doc.get('customer')]
            })
        if doc.get('vehicle'):
            internal_links_found.append({
                'doctype': 'Customer Vehicle',
                'count': 1,
                'open_count': 0,
                'names': [doc.get('vehicle')]
            })
        if doc.get('job_order'):
            internal_links_found.append({
                'doctype': 'Vehicle Job Order',
                'count': 1,
                'open_count': 0,
                'names': [doc.get('job_order')]
            })
            
        for dt, fld in [
            ('Vehicle Job Order', 'estimate'),
            ('Quotation', 'custom_vehicle_estimate')
        ]:
            if not items or dt in items:
                cnt = 0
                try:
                    meta = frappe.get_meta(dt)
                    if meta.has_field(fld):
                        cnt = len(frappe.get_all(dt, filters={fld: name}, limit=100))
                except Exception:
                    cnt = 0
                external_links_found.append({
                    'doctype': dt,
                    'count': cnt,
                    'open_count': 0
                })

    elif doctype == 'Customer Vehicle':
        if doc.get('customer'):
            internal_links_found.append({
                'doctype': 'Customer',
                'count': 1,
                'open_count': 0,
                'names': [doc.get('customer')]
            })
        for dt, fld in [
            ('Vehicle Job Order', 'vehicle'),
            ('Vehicle Estimate', 'vehicle'),
            ('Vehicle Inspection', 'vehicle'),
            ('Sales Invoice', 'custom_vehicle_plate')
        ]:
            if not items or dt in items:
                cnt = 0
                try:
                    meta = frappe.get_meta(dt)
                    if meta.has_field(fld):
                        cnt = len(frappe.get_all(dt, filters={fld: name}, limit=100))
                except Exception:
                    cnt = 0
                external_links_found.append({
                    'doctype': dt,
                    'count': cnt,
                    'open_count': 0
                })

frappe.response['message'] = {
    'count': {
        'internal_links_found': internal_links_found,
        'external_links_found': external_links_found
    }
}
"""

ss_name = "VM Safe Open Count API"
ss_payload = {
    'name': ss_name,
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_get_open_count',
    'allow_guest': 0,
    'disabled': 0,
    'script': server_script_code
}

req = urllib.request.Request(f"{URL}/api/resource/Server%20Script/{urllib.parse.quote(ss_name)}", data=urllib.parse.urlencode({'data': json.dumps(ss_payload)}).encode(), headers=H)
try:
    req.get_method = lambda: 'PUT'
    op.open(req)
except Exception:
    req = urllib.request.Request(f"{URL}/api/resource/Server%20Script", data=urllib.parse.urlencode({'data': json.dumps(ss_payload)}).encode(), headers=H)
    op.open(req)
print("Updated Server Script 'VM Safe Open Count API'")


# 2. Update Client Script to ensure Dashboard connects to vm_get_open_count and fixes links
client_script_content = """(function() {
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

  // Dashboard link and open-count fixer for Vehicle Management doctypes
  function patchVMDashboard(frm) {
    if (!frm || !frm.doctype) return;
    
    if (frm.doctype === "Vehicle Job Order") {
      if (frm.meta && frm.meta.__dashboard) {
        frm.meta.__dashboard.method = "vm_get_open_count";
        frm.meta.__dashboard.internal_links = {
          "Customer Vehicle": "vehicle",
          "Customer": "customer",
          "Vehicle Estimate": "estimate"
        };
        if (frm.meta.__dashboard.non_standard_fieldnames) {
          delete frm.meta.__dashboard.non_standard_fieldnames["Customer"];
          delete frm.meta.__dashboard.non_standard_fieldnames["Customer Vehicle"];
        }
      }
      if (frm.dashboard && frm.dashboard.data) {
        frm.dashboard.data.method = "vm_get_open_count";
        frm.dashboard.data.internal_links = {
          "Customer Vehicle": "vehicle",
          "Customer": "customer",
          "Vehicle Estimate": "estimate"
        };
        if (frm.dashboard.data.non_standard_fieldnames) {
          delete frm.dashboard.data.non_standard_fieldnames["Customer"];
          delete frm.dashboard.data.non_standard_fieldnames["Customer Vehicle"];
        }
      }
    } else if (frm.doctype === "Vehicle Estimate") {
      if (frm.meta && frm.meta.__dashboard) {
        frm.meta.__dashboard.method = "vm_get_open_count";
        frm.meta.__dashboard.internal_links = {
          "Customer Vehicle": "vehicle",
          "Customer": "customer",
          "Vehicle Job Order": "job_order"
        };
        if (frm.meta.__dashboard.non_standard_fieldnames) {
          delete frm.meta.__dashboard.non_standard_fieldnames["Customer"];
          delete frm.meta.__dashboard.non_standard_fieldnames["Customer Vehicle"];
        }
      }
      if (frm.dashboard && frm.dashboard.data) {
        frm.dashboard.data.method = "vm_get_open_count";
        frm.dashboard.data.internal_links = {
          "Customer Vehicle": "vehicle",
          "Customer": "customer",
          "Vehicle Job Order": "job_order"
        };
        if (frm.dashboard.data.non_standard_fieldnames) {
          delete frm.dashboard.data.non_standard_fieldnames["Customer"];
          delete frm.dashboard.data.non_standard_fieldnames["Customer Vehicle"];
        }
      }
    } else if (frm.doctype === "Customer Vehicle") {
      if (frm.meta && frm.meta.__dashboard) {
        frm.meta.__dashboard.method = "vm_get_open_count";
        frm.meta.__dashboard.internal_links = {
          "Customer": "customer"
        };
      }
      if (frm.dashboard && frm.dashboard.data) {
        frm.dashboard.data.method = "vm_get_open_count";
        frm.dashboard.data.internal_links = {
          "Customer": "customer"
        };
      }
    }
  }

  // Hook into form setup and refresh
  $(document).on("form-load form-refresh", function(e, frm) {
    patchVMDashboard(frm);
  });

  if (window.frappe && frappe.ui && frappe.ui.form) {
    frappe.ui.form.on("Vehicle Job Order", {
      setup: function(frm) { patchVMDashboard(frm); },
      refresh: function(frm) { patchVMDashboard(frm); }
    });
    frappe.ui.form.on("Vehicle Estimate", {
      setup: function(frm) { patchVMDashboard(frm); },
      refresh: function(frm) { patchVMDashboard(frm); }
    });
    frappe.ui.form.on("Customer Vehicle", {
      setup: function(frm) { patchVMDashboard(frm); },
      refresh: function(frm) { patchVMDashboard(frm); }
    });
  }

  ensureVMBootSidebar();
  $(document).ready(ensureVMBootSidebar);
  $(document).on("toolbar_setup page-change", ensureVMBootSidebar);
})();
"""

# Update Client Script
cs_payload = {
    'name': 'VM Header Shortcut Button',
    'doctype': 'Client Script',
    'dt': 'DocType',
    'view': 'Form',
    'enabled': 1,
    'script': client_script_content
}

req = urllib.request.Request(f"{URL}/api/resource/Client%20Script/{urllib.parse.quote('VM Header Shortcut Button')}", data=urllib.parse.urlencode({'data': json.dumps(cs_payload)}).encode(), headers=H)
req.get_method = lambda: 'PUT'
op.open(req)
print("Updated Client Script 'VM Header Shortcut Button'")

# Also update the local JS file in the repo
local_js = r"c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\public\js\vehicle_management_desk.js"
with open(local_js, "w", encoding="utf-8") as f:
    f.write(client_script_content)
print(f"Updated local repo JS: {local_js}")
"""
"""
