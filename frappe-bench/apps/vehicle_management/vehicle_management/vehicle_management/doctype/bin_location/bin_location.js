// Copyright (c) 2026, Autometrik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bin Location", {
	warehouse(frm) {
		if (frm.doc.warehouse) {
			frappe.db.get_value("Warehouse", frm.doc.warehouse, "company", (r) => {
				if (r && r.company) {
					frm.set_value("company", r.company);
				}
			});
		}
	}
});
