// Copyright (c) 2026, Autometrik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Estimate", {
	refresh(frm) {
		if (!frm.is_new()) {
			// Action button to convert to Job Order
			if (!frm.doc.job_order && frm.doc.status !== "Cancelled" && frm.doc.status !== "Declined") {
				frm.add_custom_button(__("Create Job Order"), () => {
					frappe.confirm(__("Convert this Estimate into a Vehicle Job Order?"), () => {
						frappe.call({
							doc: frm.doc,
							method: "make_job_order",
							freeze: true,
							freeze_message: __("Creating Vehicle Job Order..."),
							callback: (r) => {
								if (r.message) {
									frappe.set_route("Form", "Vehicle Job Order", r.message);
								}
							}
						});
					});
				}, __("Actions")).addClass("btn-primary");
			} else if (frm.doc.job_order) {
				frm.add_custom_button(__("View Job Order: {0}", [frm.doc.job_order]), () => {
					frappe.set_route("Form", "Vehicle Job Order", frm.doc.job_order);
				}, __("Actions"));
			}

			// Dashboard indicators
			const status_colors = {
				"Draft": "gray",
				"Sent": "blue",
				"Approved": "green",
				"Declined": "red",
				"Converted to Job Order": "purple",
				"Expired": "orange",
				"Cancelled": "darkgray"
			};
			frm.dashboard.add_indicator(
				__("Status: {0}", [frm.doc.status || "Draft"]),
				status_colors[frm.doc.status] || "gray"
			);

			if (frm.doc.grand_total) {
				frm.dashboard.add_indicator(
					__("Estimated Total: {0}", [format_currency(frm.doc.grand_total)]),
					"blue"
				);
			}
		}
	},

	vehicle(frm) {
		if (frm.doc.vehicle) {
			frappe.db.get_doc("Customer Vehicle", frm.doc.vehicle).then(veh => {
				frm.set_value({
					plate_no: veh.plate_no,
					make: veh.make,
					model: veh.model,
					year_model: veh.year_model,
					vin: veh.vin,
					engine_no: veh.engine_no,
					color: veh.color,
					mileage: veh.current_mileage || veh.latest_odometer,
					mileage_unit: veh.mileage_unit || "km",
					customer: veh.customer,
					customer_name: veh.customer_name,
					contact_no: veh.contact_no,
					email: veh.email
				});
			});
		}
	},

	discount_amount(frm) {
		calculate_estimate_totals(frm);
	}
});

frappe.ui.form.on("Job Order Service Item", {
	service_item(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.service_item) {
			frappe.db.get_value("Item", row.service_item, ["item_name", "standard_rate", "description"], (r) => {
				if (r) {
					frappe.model.set_value(cdt, cdn, "description", r.description || r.item_name || row.service_item);
					if (r.standard_rate && !row.rate) {
						frappe.model.set_value(cdt, cdn, "rate", r.standard_rate);
					}
				}
			});
		}
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
		calculate_estimate_totals(frm);
	}
});

frappe.ui.form.on("Job Order Part Item", {
	item_code(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.item_code) {
			frappe.db.get_value("Item", row.item_code, ["item_name", "stock_uom", "standard_rate"], (r) => {
				if (r) {
					frappe.model.set_value(cdt, cdn, "item_name", r.item_name || row.item_code);
					frappe.model.set_value(cdt, cdn, "uom", r.stock_uom || "PC");
					if (r.standard_rate && !row.rate) {
						frappe.model.set_value(cdt, cdn, "rate", r.standard_rate);
					}
				}
			});
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
		calculate_estimate_totals(frm);
	}
});

function calculate_service_row(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	const hours = flt(row.hours) || 1.0;
	const rate = flt(row.rate);
	const disc = flt(row.discount_amount);
	const total = Math.max(0, (hours * rate) - disc);
	frappe.model.set_value(cdt, cdn, "total_amount", total);
	calculate_estimate_totals(frm);
}

function calculate_part_row(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	const qty = flt(row.qty) || 1.0;
	const rate = flt(row.rate);
	const disc = flt(row.discount_amount);
	const total = Math.max(0, (qty * rate) - disc);
	frappe.model.set_value(cdt, cdn, "amount", total);
	calculate_estimate_totals(frm);
}

function calculate_estimate_totals(frm) {
	let total_labor = 0.0;
	(frm.doc.services || []).forEach(s => {
		total_labor += flt(s.total_amount);
	});

	let total_parts = 0.0;
	(frm.doc.parts || []).forEach(p => {
		total_parts += flt(p.amount);
	});

	const net_total = total_labor + total_parts;
	const grand_total = Math.max(0, net_total - flt(frm.doc.discount_amount));

	frm.set_value("total_labor", total_labor);
	frm.set_value("total_parts", total_parts);
	frm.set_value("net_total", net_total);
	frm.set_value("grand_total", grand_total);
}
