frappe.pages['vehicle_relationship_map'].on_page_load = function(wrapper) {
  var page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'SAP Business One Relationship Map',
    single_column: true
  });

  page.set_title_sub('Interactive Vehicle Management Document & Accounting Graph');

  const $body = $(page.body);
  $body.html('<div id="sap_page_map_container" style="height: calc(100vh - 120px); width: 100%;"></div>');

  // Check URL parameters for doctype and docname
  const params = frappe.get_route();
  let doctype = "Vehicle Job Order";
  let docname = "";

  if (frappe.route_options) {
    doctype = frappe.route_options.doctype || doctype;
    docname = frappe.route_options.docname || docname;
  }

  // Load SAP Relationship Map viewer
  function startViewer() {
    if (window.SAPRelationshipMap && window.SAPRelationshipMap.open) {
      const container = document.getElementById("sap_page_map_container");
      new window.SAPRelationshipMap.ViewerClass({
        doctype: doctype,
        docname: docname,
        container: container,
        isModal: false
      });
    } else {
      setTimeout(startViewer, 100);
    }
  }

  startViewer();
};
