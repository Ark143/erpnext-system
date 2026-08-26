// Copyright (c) 2026, Autometrik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer", {
	refresh(frm) {
		if (!frm.is_new()) {
			// Quick Action Buttons
			frm.add_custom_button(__("Register Vehicle"), () => {
				frappe.new_doc("Customer Vehicle", {
					customer: frm.doc.name,
					customer_name: frm.doc.customer_name,
					contact_no: frm.doc.custom_mobile_no || frm.doc.mobile_no,
					email: frm.doc.custom_email_address || frm.doc.email_id
				});
			}, __("Vehicle Actions"));

			frm.add_custom_button(__("New Job Order"), () => {
				frappe.new_doc("Vehicle Job Order", {
					customer: frm.doc.name,
					customer_name: frm.doc.customer_name,
					contact_no: frm.doc.custom_mobile_no || frm.doc.mobile_no
				});
			}, __("Vehicle Actions"));

			frm.add_custom_button(__("View Vehicles ({0})", [frm.doc.__vehicles_count || 0]), () => {
				frappe.set_route("List", "Customer Vehicle", { customer: frm.doc.name });
			}, __("Vehicle Actions"));

			frm.add_custom_button(__("Service History"), () => {
				frappe.set_route("List", "Vehicle Job Order", { customer: frm.doc.name });
			}, __("Vehicle Actions"));
		}
	},

	custom_first_name(frm) {
		sync_individual_name(frm);
	},

	custom_last_name(frm) {
		sync_individual_name(frm);
	}
});

function sync_individual_name(frm) {
	if (frm.doc.customer_type === "Individual") {
		let first = (frm.doc.custom_first_name || "").trim();
		let last = (frm.doc.custom_last_name || "").trim();
		if (first || last) {
			let full = `${first} ${last}`.trim();
			frm.set_value("customer_name", full);
		}
	}
}
