// Copyright (c) 2026, Autometrik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Inspection", {
	inspection_template(frm) {
		if (frm.doc.inspection_template) {
			frappe.call({
				doc: frm.doc,
				method: "load_template_items",
				callback: function(r) {
					frm.refresh_field("items");
				}
			});
		}
	},

	refresh(frm) {
		if (frm.doc.vehicle) {
			frm.add_custom_button(__("View Vehicle"), () => {
				frappe.set_route("Form", "Customer Vehicle", frm.doc.vehicle);
			}, __("Links"));
		}
	}
});
