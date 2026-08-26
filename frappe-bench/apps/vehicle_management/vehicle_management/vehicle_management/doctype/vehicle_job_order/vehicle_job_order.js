// Copyright (c) 2026, Autometrik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Job Order", {
	onload(frm) {
		if (frm.is_new() && !frm.doc.time_in) {
			frm.set_value("time_in", frappe.datetime.now_datetime());
		}
	},

	refresh(frm) {
		// Custom Action Buttons
		if (frm.doc.docstatus === 1 && !frm.doc.sales_invoice) {
			frm.add_custom_button(__("Create Sales Invoice"), () => {
				frappe.call({
					doc: frm.doc,
					method: "make_sales_invoice",
					freeze: true,
					callback: function(r) {
						frm.reload_doc();
					}
				});
			}, __("Actions"));
		}

		if (frm.doc.sales_invoice) {
			frm.add_custom_button(__("View Sales Invoice"), () => {
				frappe.set_route("Form", "Sales Invoice", frm.doc.sales_invoice);
			}, __("Actions"));
		}

		if (frm.doc.vehicle) {
			frm.add_custom_button(__("View Vehicle"), () => {
				frappe.set_route("Form", "Customer Vehicle", frm.doc.vehicle);
			}, __("Links"));
		}

		if (frm.doc.estimate) {
			frm.add_custom_button(__("View Estimate"), () => {
				frappe.set_route("Form", "Vehicle Estimate", frm.doc.estimate);
			}, __("Links"));
		}

		// Quick Timestamps buttons
		if (!frm.doc.__islocal && frm.doc.docstatus === 0) {
			if (!frm.doc.work_start_time) {
				frm.add_custom_button(__("Start Work"), () => {
					frm.set_value("work_start_time", frappe.datetime.now_datetime());
					frm.set_value("status", "In Progress");
					frm.save();
				}, __("Time Tracking"));
			} else if (!frm.doc.work_end_time) {
				frm.add_custom_button(__("Complete Work"), () => {
					frm.set_value("work_end_time", frappe.datetime.now_datetime());
					frm.set_value("status", "Completed");
					frm.save();
				}, __("Time Tracking"));
			}

			if (!frm.doc.time_out) {
				frm.add_custom_button(__("Set Time Out"), () => {
					frm.set_value("time_out", frappe.datetime.now_datetime());
					frm.save();
				}, __("Time Tracking"));
			}
		}
	},

	discount_amount(frm) {
		calculate_grand_total(frm);
	}
});

frappe.ui.form.on("Job Order Service Item", {
	services_add(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (!row.start_time) {
			frappe.model.set_value(cdt, cdn, "start_time", frappe.datetime.now_datetime());
		}
	},
	start_time(frm, cdt, cdn) {
		calculate_service_duration(frm, cdt, cdn);
	},
	end_time(frm, cdt, cdn) {
		calculate_service_duration(frm, cdt, cdn);
	},
	hours(frm, cdt, cdn) {
		calculate_service_row(frm, cdt, cdn);
	},
	rate(frm, cdt, cdn) {
		calculate_service_row(frm, cdt, cdn);
	},
	discount_amount(frm, cdt, cdn) {
		calculate_service_row(frm, cdt, cdn);
	},
	services_remove(frm) {
		calculate_grand_total(frm);
	}
});

frappe.ui.form.on("Job Order Part Item", {
	parts_add(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (!row.issued_time) {
			frappe.model.set_value(cdt, cdn, "issued_time", frappe.datetime.now_datetime());
		}
	},
	qty(frm, cdt, cdn) {
		calculate_part_row(frm, cdt, cdn);
	},
	rate(frm, cdt, cdn) {
		calculate_part_row(frm, cdt, cdn);
	},
	discount_amount(frm, cdt, cdn) {
		calculate_part_row(frm, cdt, cdn);
	},
	parts_remove(frm) {
		calculate_grand_total(frm);
	}
});

function calculate_service_duration(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.start_time && row.end_time) {
		let start = new Date(row.start_time);
		let end = new Date(row.end_time);
		let diffHours = (end - start) / (1000 * 60 * 60);
		if (diffHours > 0) {
			frappe.model.set_value(cdt, cdn, "hours", Math.round(diffHours * 100) / 100);
			return;
		}
	}
	calculate_service_row(frm, cdt, cdn);
}

function calculate_service_row(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let hours = flt(row.hours) || 1.0;
	let rate = flt(row.rate);
	let disc = flt(row.discount_amount);
	row.total_amount = Math.max(0, (hours * rate) - disc);
	frm.refresh_field("services");
	calculate_grand_total(frm);
}

function calculate_part_row(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let qty = flt(row.qty) || 1.0;
	let rate = flt(row.rate);
	let disc = flt(row.discount_amount);
	row.amount = Math.max(0, (qty * rate) - disc);
	frm.refresh_field("parts");
	calculate_grand_total(frm);
}

function calculate_grand_total(frm) {
	let total_labor = 0.0;
	(frm.doc.services || []).forEach(row => {
		total_labor += flt(row.total_amount);
	});
	frm.set_value("total_labor", total_labor);

	let total_parts = 0.0;
	(frm.doc.parts || []).forEach(row => {
		total_parts += flt(row.amount);
	});
	frm.set_value("total_parts", total_parts);

	let net_total = total_labor + total_parts;
	frm.set_value("net_total", net_total);

	let disc = flt(frm.doc.discount_amount);
	frm.set_value("grand_total", Math.max(0, net_total - disc));

	frm.refresh_field("total_labor");
	frm.refresh_field("total_parts");
	frm.refresh_field("net_total");
	frm.refresh_field("grand_total");
}
