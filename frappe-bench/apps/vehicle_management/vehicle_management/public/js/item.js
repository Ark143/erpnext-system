// Copyright (c) 2026, Autometrik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item", {
	refresh(frm) {
		// Filter model in child table by make
		frm.fields_dict["custom_vehicle_compatibility"].grid.get_field("model").get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];
			return {
				filters: {
					make: row.make || ""
				}
			};
		};
	},

	custom_purchase_cost(frm) {
		calculate_pricing(frm);
	},

	custom_pricing_rule(frm) {
		let rule = frm.doc.custom_pricing_rule;
		if (rule === "MARK-UP 50%") {
			frm.set_value("custom_markup_rate", 50.0);
		} else if (rule === "MARK-UP 30%") {
			frm.set_value("custom_markup_rate", 30.0);
		} else if (rule === "MARK-UP 20%") {
			frm.set_value("custom_markup_rate", 20.0);
		} else if (rule === "MARK-UP 15%") {
			frm.set_value("custom_markup_rate", 15.0);
		}
		calculate_pricing(frm);
	},

	custom_markup_rate(frm) {
		calculate_pricing(frm);
	},

	custom_sell_price(frm) {
		let cost = flt(frm.doc.custom_purchase_cost);
		let sell = flt(frm.doc.custom_sell_price);
		if (sell > 0 && cost > 0) {
			let margin = ((sell - cost) / sell) * 100.0;
			frm.set_value("custom_margin_percent", margin);
		}
	}
});

frappe.ui.form.on("Item Vehicle Compatibility", {
	make(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "model", "");
	}
});

function calculate_pricing(frm) {
	let cost = flt(frm.doc.custom_purchase_cost);
	let markup = flt(frm.doc.custom_markup_rate);
	if (cost > 0) {
		let sell = cost * (1.0 + (markup / 100.0));
		frm.set_value("custom_sell_price", sell);
		let margin = sell > 0 ? ((sell - cost) / sell) * 100.0 : 0.0;
		frm.set_value("custom_margin_percent", margin);
	}
}
