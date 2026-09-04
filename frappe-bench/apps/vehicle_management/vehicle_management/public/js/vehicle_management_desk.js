(function() {
  const VM_SIDEBAR_ITEMS = [
    { label: "Vehicle Management", link_to: "Vehicle Management", link_type: "Workspace", type: "Link", icon: "home", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
    { label: "SAP Relationship Map", link_to: "vehicle_relationship_map", link_type: "Page", type: "Link", icon: "sitemap", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },
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
    { label: "Monthly Job Orders", link_to: "Monthly Job Orders", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Vehicle Job Order" } },
    { label: "Detailed Job Orders", link_to: "Detailed Job Orders", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Vehicle Job Order" } },
    { label: "Top Vehicles Served", link_to: "Top Vehicles Served", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Vehicle Job Order" } },
    { label: "Check Register", link_to: "Check Register", link_type: "Report", type: "Link", icon: "table", child: 1, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0, report: { report_type: "Script Report", ref_doctype: "Payment Entry" } },
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

  ensureVMBootSidebar();
  $(document).ready(ensureVMBootSidebar);
  $(document).on("toolbar_setup page-change", ensureVMBootSidebar);

  // ─────────────────────────────────────────────
  // Inject SAP Relationship Map Button on Forms
  // ─────────────────────────────────────────────
  const MAP_SUPPORTED_DOCTYPES = [
    "Vehicle Job Order",
    "Vehicle Estimate",
    "Vehicle Inspection",
    "Customer Vehicle",
    "Vehicle POS Invoice",
    "Sales Invoice",
    "POS Invoice",
    "Stock Entry",
    "Payment Entry",
    "Quotation"
  ];

  function injectRelationshipMapButton(frm) {
    if (!frm || !frm.doc || !frm.doc.name || frm.doc.__islocal) return;
    if (!MAP_SUPPORTED_DOCTYPES.includes(frm.doctype)) return;

    // Check if button already added
    if (frm.page && !frm.page.has_sap_map_btn) {
      frm.page.add_inner_button(__('🗺️ SAP Relationship Map'), function() {
        if (window.SAPRelationshipMap && window.SAPRelationshipMap.open) {
          window.SAPRelationshipMap.open({
            doctype: frm.doctype,
            docname: frm.doc.name,
            vehicle: frm.doc.vehicle || frm.doc.plate_no || frm.doc.custom_vehicle_plate || "",
            customer: frm.doc.customer || frm.doc.party_name || ""
          });
        } else {
          frappe.msgprint(__('Loading Relationship Map module...'));
        }
      }, __('View')).addClass('btn-sap-relationship-map');

      frm.page.has_sap_map_btn = true;
    }
  }

  // Hook into frappe.ui.form.on for all supported doctypes
  MAP_SUPPORTED_DOCTYPES.forEach(function(dt) {
    frappe.ui.form.on(dt, {
      refresh: function(frm) {
        injectRelationshipMapButton(frm);
      }
    });
  });

})();
