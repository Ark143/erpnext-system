// Copyright (c) 2026, Autometrik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Model", {
	refresh(frm) {
	},
	model_name(frm) {
		if (frm.doc.model_name) {
			frm.set_value("model_name", frm.doc.model_name.trim().toUpperCase());
		}
	},
	make(frm) {
		if (frm.doc.make) {
			frm.set_value("make", frm.doc.make.trim().toUpperCase());
		}
	},
	validate(frm) {
		if (frm.doc.model_name) {
			frm.doc.model_name = frm.doc.model_name.trim().toUpperCase();
		}
		if (frm.doc.make) {
			frm.doc.make = frm.doc.make.trim().toUpperCase();
		}
	}
});
