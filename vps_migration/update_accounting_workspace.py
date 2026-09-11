import requests, json

BASE_URL = 'http://38.247.138.224:10017'

def main():
    s = requests.Session()
    r = s.post(f'{BASE_URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})
    if r.status_code != 200:
        print('Login failed:', r.status_code)
        return

    print('Logged in successfully to ERPNext!')

    # -------------------------------------------------------------
    # 1. Update Financial Reports Workspace
    # -------------------------------------------------------------
    fin_res = s.get(f'{BASE_URL}/api/resource/Workspace/Financial%20Reports')
    if fin_res.status_code == 200:
        fin_data = fin_res.json().get('data', {})
        
        # Build clean shortcuts
        fin_shortcuts = [
            {
                'type': 'URL',
                'url': '/consolidated-financials#cash_flow',
                'label': '💵 Cash Flow Statement (Daily/Monthly/Yearly)',
                'color': 'Green',
                'doc_view': ''
            },
            {
                'type': 'URL',
                'url': '/consolidated-financials#ar_aging',
                'label': '📥 AR Aging (30, 60, 90 Days)',
                'color': 'Blue',
                'doc_view': ''
            },
            {
                'type': 'URL',
                'url': '/consolidated-financials#ap_aging',
                'label': '📤 AP Aging (30, 60, 90 Days)',
                'color': 'Orange',
                'doc_view': ''
            },
            {
                'type': 'URL',
                'url': '/consolidated-financials',
                'label': '📊 Multi-Company Financials Console',
                'color': 'Purple',
                'doc_view': ''
            }
        ]
        
        # Ensure existing links have the new Card Break or keep standard ones
        links = fin_data.get('links', [])
        
        # Remove any previous custom card breaks to prevent duplicates
        links = [l for l in links if l.get('label') not in [
            'Multi-Company Financials & Cash Flow',
            '💵 Cash Flow Statement (Daily / Monthly / Yearly)',
            '📥 AR Aging Analysis (30-60-90 Days)',
            '📤 AP Aging Analysis (30-60-90 Days)',
            '📊 Consolidated Financials Console'
        ]]
        
        # Prepend new Card Break and links
        new_links = [
            {
                'type': 'Card Break',
                'label': 'Multi-Company Financials & Cash Flow',
                'link_type': 'DocType',
                'onboard': 0,
                'is_query_report': 0,
                'link_count': 4
            },
            {
                'type': 'Link',
                'label': 'Cash Flow Statement (Daily, Monthly, Yearly)',
                'link_type': 'Report',
                'link_to': 'Cash Flow',
                'dependencies': 'GL Entry',
                'is_query_report': 1,
                'onboard': 0
            },
            {
                'type': 'Link',
                'label': 'Accounts Receivable (AR) Aging',
                'link_type': 'Report',
                'link_to': 'Accounts Receivable',
                'dependencies': 'Sales Invoice',
                'is_query_report': 1,
                'onboard': 0
            },
            {
                'type': 'Link',
                'label': 'Accounts Payable (AP) Aging',
                'link_type': 'Report',
                'link_to': 'Accounts Payable',
                'dependencies': 'Purchase Invoice',
                'is_query_report': 1,
                'onboard': 0
            },
            {
                'type': 'Link',
                'label': 'Consolidated Financial Statement',
                'link_type': 'Report',
                'link_to': 'Consolidated Financial Statement',
                'dependencies': 'GL Entry',
                'is_query_report': 1,
                'onboard': 0
            }
        ] + links
        
        fin_update = {
            'shortcuts': fin_shortcuts,
            'links': new_links
        }
        
        upd_r = s.put(f'{BASE_URL}/api/resource/Workspace/Financial%20Reports', json=fin_update)
        print('Updated Financial Reports Workspace:', upd_r.status_code)

    # -------------------------------------------------------------
    # 2. Update Invoicing Workspace
    # -------------------------------------------------------------
    inv_res = s.get(f'{BASE_URL}/api/resource/Workspace/Invoicing')
    if inv_res.status_code == 200:
        inv_data = inv_res.json().get('data', {})
        existing_shortcuts = inv_data.get('shortcuts', [])
        
        # Filter out existing duplicates
        inv_shortcuts = [sc for sc in existing_shortcuts if sc.get('label') not in [
            '📥 AR Aging (30, 60, 90 Days)',
            '📤 AP Aging (30, 60, 90 Days)',
            '💵 Cash Flow Statement',
            '📊 Consolidated Financials'
        ]]
        
        # Add the shortcuts
        inv_shortcuts.insert(0, {
            'type': 'URL',
            'url': '/consolidated-financials#ar_aging',
            'label': '📥 AR Aging (30, 60, 90 Days)',
            'color': 'Blue',
            'doc_view': ''
        })
        inv_shortcuts.insert(1, {
            'type': 'URL',
            'url': '/consolidated-financials#ap_aging',
            'label': '📤 AP Aging (30, 60, 90 Days)',
            'color': 'Orange',
            'doc_view': ''
        })
        inv_shortcuts.insert(2, {
            'type': 'URL',
            'url': '/consolidated-financials#cash_flow',
            'label': '💵 Cash Flow Statement',
            'color': 'Green',
            'doc_view': ''
        })
        inv_shortcuts.insert(3, {
            'type': 'URL',
            'url': '/consolidated-financials',
            'label': '📊 Consolidated Financials',
            'color': 'Purple',
            'doc_view': ''
        })
        
        inv_update = {
            'shortcuts': inv_shortcuts
        }
        
        upd_inv = s.put(f'{BASE_URL}/api/resource/Workspace/Invoicing', json=inv_update)
        print('Updated Invoicing Workspace:', upd_inv.status_code)

    # -------------------------------------------------------------
    # 3. Update VM Header Shortcut Button Client Script for accounting Desk Sidebars & Global Navbar
    # -------------------------------------------------------------
    client_script = '''
(function() {
  const VM_SIDEBAR_ITEMS = [
    { label: "Operations", type: "Section Break", link_type: "DocType", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle POS", link_to: "vehicle_pos", link_type: "Page", type: "Link", icon: "shopping-cart", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Point of Sale", link_to: "point-of-sale", link_type: "Page", type: "Link", icon: "credit-card", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Job Orders", link_to: "Vehicle Job Order", link_type: "DocType", type: "Link", icon: "tool", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Estimates", link_to: "Vehicle Estimate", link_type: "DocType", type: "Link", icon: "file-text", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Inspections", link_to: "Vehicle Inspection", link_type: "DocType", type: "Link", icon: "check-circle", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicles", link_to: "Customer Vehicle", link_type: "DocType", type: "Link", icon: "truck", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Customers", link_to: "Customer", link_type: "DocType", type: "Link", icon: "users", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle Relationship Map", link_to: "vehicle_relationship", link_type: "Page", type: "Link", icon: "share-2", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Billing & Invoices", type: "Section Break", link_type: "DocType", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Sales Invoices", link_to: "Sales Invoice", link_type: "DocType", type: "Link", icon: "file", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "POS Invoices", link_to: "POS Invoice", link_type: "DocType", type: "Link", icon: "file-text", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Vehicle POS Invoices", link_to: "Vehicle POS Invoice", link_type: "DocType", type: "Link", icon: "file-minus", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Payments", link_to: "Payment Entry", link_type: "DocType", type: "Link", icon: "dollar-sign", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Inventory & Stock", type: "Section Break", link_type: "DocType", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Items", link_to: "Item", link_type: "DocType", type: "Link", icon: "box", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Item Vehicle Compatibility", link_to: "Item Vehicle Compatibility", link_type: "DocType", type: "Link", icon: "check-square", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Item Part Cross Reference", link_to: "Item Part Cross Reference", link_type: "DocType", type: "Link", icon: "git-commit", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Bin Locations", link_to: "Bin Location", link_type: "DocType", type: "Link", icon: "archive", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Warehouses", link_to: "Warehouse", link_type: "DocType", type: "Link", icon: "home", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Multi-Company Financials & Cash Flow", type: "Section Break", link_type: "DocType", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "💵 Cash Flow Statement", url: "/consolidated-financials#cash_flow", link_type: "Page", type: "Link", icon: "dollar-sign", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "📥 AR Aging (30/60/90 Days)", url: "/consolidated-financials#ar_aging", link_type: "Page", type: "Link", icon: "arrow-down-left", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "📤 AP Aging (30/60/90 Days)", url: "/consolidated-financials#ap_aging", link_type: "Page", type: "Link", icon: "arrow-up-right", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "📊 Consolidated Financials Console", url: "/consolidated-financials", link_type: "Page", type: "Link", icon: "bar-chart-2", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Analytical Reports", type: "Section Break", link_type: "DocType", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "Monthly Sales Report", link_to: "Monthly Sales Report", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Sales Invoice" } },
    { label: "Detailed Sales Report", link_to: "Detailed Sales Report", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Sales Invoice" } },
    { label: "Sales Analytics", link_to: "Sales Analytics", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Sales Invoice" } },
    { label: "Profit and Loss Statement", link_to: "Profit and Loss Statement", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "GL Entry" } },
    { label: "General Ledger", link_to: "General Ledger", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "GL Entry" } }
  ];

  function ensureAccountingAndVMSidebars() {
    if (window.frappe && frappe.boot) {
      if (!frappe.boot.workspace_sidebar_item) {
        frappe.boot.workspace_sidebar_item = {};
      }
      frappe.boot.workspace_sidebar_item["vehicle management"] = VM_SIDEBAR_ITEMS;
      frappe.boot.workspace_sidebar_item["Vehicle Management"] = VM_SIDEBAR_ITEMS;
    }
  }

  ensureAccountingAndVMSidebars();
  $(document).ready(ensureAccountingAndVMSidebars);
  $(document).on("toolbar_setup page-change", ensureAccountingAndVMSidebars);
})();

function addConsolidatedNavButtons() {
  if ($("#btn-consolidated-financials").length === 0 && $(".navbar-nav").length > 0) {
    const btn = $(`
      <li class="nav-item dropdown" id="btn-consolidated-financials" style="margin-right: 8px;">
        <a class="nav-link btn btn-xs btn-default dropdown-toggle" data-toggle="dropdown" href="#" style="padding: 4px 10px; font-weight: 600; font-size: 12px; background: #000; color: #fff; border: 1px solid #333; border-radius: 6px; display: inline-flex; align-items: center; gap: 5px;">
          📊 Accounting & Cash Flow <i class="fa fa-caret-down" style="font-size: 10px;"></i>
        </a>
        <ul class="dropdown-menu dropdown-menu-right" style="min-width: 250px; padding: 6px 0; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
          <li class="dropdown-header" style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #888;">Multi-Company Accounting</li>
          <li><a href="/consolidated-financials#cash_flow" target="_blank" style="padding: 8px 16px; font-size: 13px; font-weight: 500;"><span style="margin-right: 8px;">💵</span> Cash Flow (Daily/Monthly/Yearly)</a></li>
          <li><a href="/consolidated-financials#ar_aging" target="_blank" style="padding: 8px 16px; font-size: 13px; font-weight: 500;"><span style="margin-right: 8px;">📥</span> AR Aging (30, 60, 90 Days)</a></li>
          <li><a href="/consolidated-financials#ap_aging" target="_blank" style="padding: 8px 16px; font-size: 13px; font-weight: 500;"><span style="margin-right: 8px;">📤</span> AP Aging (30, 60, 90 Days)</a></li>
          <li class="divider" style="margin: 6px 0;"></li>
          <li><a href="/consolidated-financials#pnl" target="_blank" style="padding: 8px 16px; font-size: 13px; font-weight: 500;"><span style="margin-right: 8px;">📈</span> Profit & Loss Statement</a></li>
          <li><a href="/consolidated-financials#balance_sheet" target="_blank" style="padding: 8px 16px; font-size: 13px; font-weight: 500;"><span style="margin-right: 8px;">⚖️</span> Balance Sheet</a></li>
          <li><a href="/consolidated-financials#gl_explorer" target="_blank" style="padding: 8px 16px; font-size: 13px; font-weight: 500;"><span style="margin-right: 8px;">🔍</span> General Ledger Audit</a></li>
          <li class="divider" style="margin: 6px 0;"></li>
          <li><a href="/consolidated-financials" target="_blank" style="padding: 8px 16px; font-size: 13px; font-weight: 700; color: #0284c7;"><span style="margin-right: 8px;">🚀</span> Full Consolidated Console</a></li>
        </ul>
      </li>
    `);
    $(".navbar-nav.navbar-right").prepend(btn);
  }
}

$(document).ready(addConsolidatedNavButtons);
$(document).on("page-change toolbar_setup", addConsolidatedNavButtons);
'''

    cs_doc = {
        'doctype': 'Client Script',
        'dt': 'Workspace',
        'script': client_script,
        'enabled': 1
    }
    
    cs_res = s.put(f'{BASE_URL}/api/resource/Client%20Script/VM%20Header%20Shortcut%20Button', json=cs_doc)
    print('Updated VM Header Shortcut Button Client Script:', cs_res.status_code)

if __name__ == '__main__':
    main()
